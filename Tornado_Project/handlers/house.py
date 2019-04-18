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
            print(results, json.loads(results))
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
        print("datas: ", datas, tmp)
        return datas