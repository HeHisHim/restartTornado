import logging
import json
import string
import random
import re
import asyncio
import tornado.ioloop

import constants
import utils.common
from tornado.web import RequestHandler
from utils.response_code import RET
from utils.session import Session

class AreaIngoHandler(RequestHandler):
    async def get(self):
        results = None

        results = self.get_area_info_inCache()
        if results:
            results = results.decode("utf8")
            return self.write(dict(errno = RET.OK, errmsg = "OK", data = json.loads(results)))


        task = []
        task.append(asyncio.ensure_future(self.get_area_info()))

        for done in asyncio.as_completed(task):
            results = await done
        
        if not results:
            return self.write(dict(errno = RET.NODATA, errmsg = "no area data"))

        areas = []
        for result in results:
            area = {"area_id": result[0], "name": result[1]}
            areas.append(area)

        self.set_area_infoCache(areas)

        return self.write(dict(errno = RET.OK, errmsg = "OK", data = areas))

    def get_area_info_inCache(self):
        try:
            areaInfo = self.application.redis.get("area_info")
        except Exception as e:
            logging.error(e)
            areaInfo = None

        return areaInfo

    def set_area_infoCache(self, datas):
        try:
            self.application.redis.setex("area_info", constants.AREA_INFO_REDIS_EXPIRES_SECONDS, json.dumps(datas))
        except Exception as e:
            logging.error(e)

    async def get_area_info(self):
        datas = None
        SQL =  "select ai_area_id, ai_name from ih_area_info;"
        async with await self.application.db.Connection() as conn:
            try:
                async with conn.cursor() as cursor:
                    await cursor.execute(SQL)
                    datas = cursor.fetchall()
            except Exception as e:
                logging.error(e)
                return self.write(dict(errno = RET.DBERR, errmsg = "mysql查询出错"))
        return datas

class MyHouseHandler(RequestHandler):
    def get_current_user(self):
        self.user_data = dict()
        return utils.common.get_current_user(self)

    @utils.common.require_logined
    def get(self):
        uid = self.user_data.get("uid")
        results = self.get_house_info(uid)
        houses = []
        if results and results[0]:
            for result in results:
                house = {"area_id": result[0], "name": result[1]}
                house = {
                    "house_id": result[0], 
                    "title": result[1], 
                    "price": result[2],
                    "ctime": result[3].strftime("%Y-%m-%d"),
                    "area_name": result[4],
                    "img_url": None
                }
                houses.append(house)
        return self.write(dict(errno = RET.OK, errmsg = "OK", houses = houses))



    def get_house_info(self, uid):
        datas = None
        SQL = "select x.hi_house_id, x.hi_title, x.hi_price, x.hi_utime, y.ai_name, x.hi_index_image_url from ih_house_info as x left join ih_area_info as y on x.hi_area_id = y.ai_area_id where x.hi_user_id = %s;"
        with self.application.puredb.cursor() as cursor:
            try:
                cursor.execute(SQL, uid)
                datas = cursor.fetchall()
            except Exception as e:
                logging.error(e)
                return self.write(dict(errno = RET.DBERR, errmsg = "mysql出错"))
        return datas

class HouseInfoHandler(RequestHandler):
    def get_current_user(self):
        self.user_data = dict()
        return utils.common.get_current_user(self)

    def prepare(self):
        if self.request.headers.get("Content-Type") and self.request.headers.get("Content-Type").startswith("application/json"):
            self.dataBody = json.loads(self.request.body)
            if not self.dataBody:
                self.dataBody = dict()
    # 保存房屋信息
    @utils.common.require_logined
    def post(self):
        uid = self.user_data.get("uid")
        title = self.dataBody.get("title")
        price = self.dataBody.get("price")
        area_id = self.dataBody.get("area_id")
        address = self.dataBody.get("address")
        room_count = self.dataBody.get("room_count")
        acreage = self.dataBody.get("acreage")
        unit = self.dataBody.get("unit")
        capacity = self.dataBody.get("capacity")
        beds = self.dataBody.get("beds")
        deposit = self.dataBody.get("deposit")
        min_days = self.dataBody.get("min_days")
        max_days = self.dataBody.get("max_days")
        facility = self.dataBody.get("facility") # 对一个房屋的设施，是列表类型

        if not all((title, price, area_id, address, room_count, acreage, unit, capacity, beds, deposit, min_days, max_days)):
            return self.write(dict(errcode=RET.PARAMERR, errmsg="缺少参数"))

        ret = self.set_house_info(uid, title, price, area_id, address, room_count, acreage, unit, capacity, beds, deposit, min_days, max_days, facility)
        if not ret:
            return self.write(dict(errno = RET.DBERR, errmsg = "数据库错误"))
        return self.write(dict(errno = RET.OK, errmsg = "OK", house_id = ret))
        
    
    def get(self):
        pass

    def set_house_info(self, uid, title, price, area_id, address, room_count, acreage, unit, capacity, beds, deposit, min_days, max_days, facility):
        last_house_id = None
        SQL = "Insert into ih_house_info(hi_user_id, hi_title, hi_price, hi_area_id, hi_address, hi_room_count, \
                hi_acreage, hi_house_unit, hi_capacity, hi_beds,hi_deposit, hi_min_days, hi_max_days) \
                values (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);"
        with self.application.puredb.cursor() as cursor:
            try:
                cursor.execute(SQL, (uid, title, price, area_id, address, room_count, acreage, unit, capacity, beds, deposit, min_days, max_days))
                self.application.puredb.commit()
                last_house_id = cursor.lastrowid
            except Exception as e:
                logging.error(e)
                self.application.puredb.rollback()
                return self.write(dict(errno = RET.DBERR, errmsg = "mysql出错"))
        # return data
        if facility:
            vals = []
            exec_num = len(facility)

            for fid in facility:
                vals.append(last_house_id)
                vals.append(fid)

            SQL = "Insert into ih_house_facility(hf_house_id, hf_facility_id) values " + (exec_num - 1) * "(%s, %s), " + "(%s, %s);"
            with self.application.puredb.cursor() as cursor:
                try:
                    cursor.execute(SQL, args = vals)
                    self.application.puredb.commit()
                except Exception as e:
                    logging.error(e)
                    self.application.puredb.rollback()
                    return self.write(dict(errno = RET.DBERR, errmsg = "mysql出错"))

        return last_house_id



