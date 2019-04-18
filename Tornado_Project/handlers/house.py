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
                    tmp = await cursor.execute(SQL)
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
