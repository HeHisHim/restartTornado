import logging
import json
import string
import random
import re
import asyncio
import tornado.ioloop
import math

import constants
import utils.common
from tornado.web import RequestHandler
from utils.response_code import RET
from utils.session import Session
from .logic import LogicBaseHandler

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

        facility = json.dumps(facility)
        ret = self.set_house_info(uid, title, price, area_id, address, room_count, acreage, unit, capacity, beds, deposit, min_days, max_days, facility)
        if not ret:
            return self.write(dict(errno = RET.DBERR, errmsg = "数据库错误"))
        return self.write(dict(errno = RET.OK, errmsg = "OK", house_id = ret))
        
    @utils.common.require_logined
    def get(self):
        uid = self.user_data.get("uid")
        uid = self.get_argument("uid")
        res = self.get_house_info(uid)

        if not res:
            return 
        
        res = json.loads(res[0])

    def set_house_info(self, uid, title, price, area_id, address, room_count, acreage, unit, capacity, beds, deposit, min_days, max_days, facility):
        last_house_id = None
        SQL = "Insert into ih_house_info(hi_user_id, hi_title, hi_price, hi_area_id, hi_address, hi_room_count, \
                hi_acreage, hi_house_unit, hi_capacity, hi_beds,hi_deposit, hi_min_days, hi_max_days, hi_facility) \
                values (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);"
        with self.application.puredb.cursor() as cursor:
            try:
                cursor.execute(SQL, (uid, title, price, area_id, address, room_count, acreage, unit, capacity, beds, deposit, min_days, max_days, facility))
                self.application.puredb.commit()
                last_house_id = cursor.lastrowid
            except Exception as e:
                logging.error(e)
                self.application.puredb.rollback()
                return self.write(dict(errno = RET.DBERR, errmsg = "mysql出错"))
        return last_house_id

    def get_house_info(self, uid):
        datas = None
        SQL = "select hi_facility from ih_house_info where hi_user_id = %s;"
        with self.application.puredb.cursor() as cursor:
            try:
                cursor.execute(SQL, uid)
                datas = cursor.fetchone()
            except Exception as e:
                logging.error(e)
                return self.write(dict(errno = RET.DBERR, errmsg = "mysql出错"))
        return datas


class HouseListHandler(LogicBaseHandler):
    async def get(self):
        # 获取参数
        start_date = self.get_argument("sd", "")
        end_date = self.get_argument("ed", "")
        aid = self.get_argument("aid", "")
        sort_key = self.get_argument("sk", "new") # 最新上线, 入住最多, 价格低-高, 价格高-低
        page = self.get_argument("page", "1")
        task = []
        resHouses = []
        pageCount = 0
        theKey = "house_info_%s_%s_%s_%s" % (start_date, end_date, aid, sort_key)
        # 校验
        page = int(page)

        redisRes = self.get_houseList_inRedis(theKey, str(page))
        pageCount = self.get_houseList_inRedis(theKey, "total")
        if redisRes:
            redisRes = redisRes.decode("utf8")
            return self.write(dict(errno = RET.OK, errmsg = "OK", total_page = pageCount.decode("utf8"), data = json.loads(redisRes)))

        task.append(asyncio.ensure_future(self.get_houseInfo_index(start_date, end_date, aid, sort_key, page)))
        task.append(asyncio.ensure_future(self.get_all_houseInfo()))
        for done in asyncio.as_completed(task):
            result = await done
            if isinstance(result, tuple):
                for res in result:
                    house = {
                        "house_id": res[0],
                        "title": res[1],
                        "price": res[2],
                        "room_count": res[3],
                        "address": res[4],
                        "order_count": res[5],
                        "avatar_url": res[6],
                        "img_url": res[7],
                    }
                    resHouses.append(house)

            elif isinstance(result, int):
                pageCount = math.ceil(result / constants.HOME_PAGE_MAX_HOUSES * 1.0)

        pageDatas = resHouses[:constants.HOUSE_LIST_PAGE_CAPACITY]

        self.set_houseList_inRedis(theKey, page, resHouses, pageCount)

        return self.write(dict(errno = RET.OK, errmsg = "OK", total_page = pageCount, data = pageDatas))
        
    async def get_houseInfo_index(self, start_date, end_date, aid, sort_key, page):
        dateSQL = areaSQL = ""
        self.whereSQL = []
        self.SQL_params = {}
        datas = None

        # 查询 ih_house_info, ih_user_profile, ih_order_info
        SQL = "Select distinct hi_house_id, hi_title, hi_price, hi_room_count, hi_address, hi_order_count, up_avatar, hi_index_image_url, hi_utime \
                from ih_house_info as x left join ih_order_info as y on x.hi_house_id = y.oi_house_id \
                join ih_user_profile as z on x.hi_user_id = z.up_user_id "
        if start_date and end_date:
            dateSQL = "(y.oi_begin_date is null and y.oi_end_date is null) or (not (y.oi_begin_date <= %(end_date)s and y.oi_end_date >= %(start_date)s))"
            self.SQL_params["start_date"] = start_date
            self.SQL_params["end_date"] = end_date
            self.whereSQL.append(dateSQL)
        elif start_date:
            dateSQL = "(y.oi_begin_date is null and y.oi_end_date is null) or (y.oi_end_date < %(start_date)s)"
            self.SQL_params["start_date"] = start_date
            self.whereSQL.append(dateSQL)
        elif end_date:
            dateSQL = "(y.oi_begin_date is null and y.oi_end_date is null) or (y.oi_begin_date > %(end_date)s)"
            self.SQL_params["end_date"] = end_date
            self.whereSQL.append(dateSQL)
        if aid:
            areaSQL = "x.hi_area_id = %(aid)s"
            self.SQL_params["aid"] = aid
            self.whereSQL.append(areaSQL)

        if self.whereSQL:
            SQL += " where "
            SQL += " and ".join(self.whereSQL)
        if "hot" == sort_key:
            SQL += " order by x.hi_order_count desc"
        elif "pri-inc" == sort_key:
            SQL += " order by x.hi_prece asc"
        elif "pri-des" == sort_key:
            SQL += " order by x.hi_prece desc"
        else:
            SQL += " order by x.hi_utime desc"

        if 1 == page:
            SQL += " limit %d" % (constants.HOUSE_LIST_PAGE_CAPACITY * constants.HOME_LIST_REIDS_CACHED_PAGE)
        else:
            SQL += " limit %d, %d" % ((page - 1) * constants.HOUSE_LIST_PAGE_CAPACITY * constants.HOME_LIST_REIDS_CACHED_PAGE, constants.HOUSE_LIST_PAGE_CAPACITY * constants.HOME_LIST_REIDS_CACHED_PAGE)

        async with await self.application.db.Connection() as conn:
            try:
                async with conn.cursor() as cursor:
                    await cursor.execute(SQL, self.SQL_params)
                    datas = cursor.fetchall()
            except Exception as e:
                logging.error(e)
                return self.write(dict(errno = RET.DBERR, errmsg = "mysql查询出错"))
        return datas

    async def get_all_houseInfo(self):
        res = 0
        SQL = "Select count(distinct x.hi_house_id) from ih_house_info as x left join ih_order_info as y on x.hi_house_id = y.oi_house_id "
        if self.whereSQL:
            SQL += " where "
            SQL += " and ".join(self.whereSQL) 
        async with await self.application.db.Connection() as conn:
            try:
                async with conn.cursor() as cursor:
                    await cursor.execute(SQL, self.SQL_params)
                    res = int(cursor.fetchone()[0])
            except Exception as e:
                logging.error(e)
                return self.write(dict(errno = RET.DBERR, errmsg = "mysql查询出错"))
        return res
    
    def set_houseList_inRedis(self, theKey, innerKey, allDatas, total):
        saveMe = {}
        arr = []
        for data in allDatas:
            if constants.HOUSE_LIST_PAGE_CAPACITY == len(arr):
                saveMe[str(innerKey)] = json.dumps(arr)
                innerKey += 1
                arr = []
            arr.append(data)
        else:
            saveMe[str(innerKey)] = json.dumps(arr)
        saveMe["total"] = total

        try:
            self.application.redis.hmset(theKey, saveMe)
        except Exception as e:
            logging.error(e)

    def get_houseList_inRedis(self, theKey, innerKey):
        try:
            res = self.application.redis.hget(theKey, innerKey)
        except Exception as e:
            logging.error(e)
            # return self.write(dict(errno = RET.DBERR, errmsg = "redis查询出错"))
        return res