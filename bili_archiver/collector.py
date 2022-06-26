from typing import List
from bili_archiver import recorder
from bili_archiver.api import BiliAPI
from bili_archiver.logger import logger
from datetime import datetime


def collect(
        api: BiliAPI,
        from_history: bool = False,
        from_self_favorite_folders: bool = False,
        from_user_ids: List[int] = None,
):
    if from_history:
        logger.info('collecting videos from history')

        last_time = recorder.get_last_collect_time('history')
        vs = api.get_history(after=last_time)

        # 排除番剧
        vs = [v for v in vs if v['history']['bvid'] != '']

        cnt = 0
        for v in vs:
            vid = v['kid']
            is_collected = recorder.is_collected(vid)
            if not is_collected:
                cnt += 1
                recorder.download_history_set(vid)

        logger.info(f'{len(vs)} in history since {last_time}, {cnt} collected')
        recorder.set_last_collect_time('history', datetime.now())

    if from_self_favorite_folders:
        logger.info('collecting videos from favorite folders')
        folders = api.get_self_favorite_folders()
        for folder in folders:
            logger.info(f"collecting videos from favorite folder {folder['title']}")

            last_time = recorder.get_last_collect_time(f"fld{folder['id']}")
            vs = api.get_videos_of_favorite_folder(folder['id'], last_time)

            cnt = 0
            for v in vs:
                vid = v['id']
                is_collected = recorder.is_collected(vid)
                if not is_collected:
                    cnt += 1
                    recorder.download_history_set(vid)

            logger.info(f"{len(vs)} in folder {folder['title']} since {last_time}, {cnt} collected")
            recorder.set_last_collect_time(f"fld{folder['id']}")

    if from_user_ids is not None:
        for user in from_user_ids:
            logger.info('collecting videos from history')

            last_time = recorder.get_last_collect_time(f"usr{user}")
            vs = api.get_videos_of_user(user, last_time)

            cnt = 0
            for v in vs:
                vid = v['id']
                is_collected = recorder.is_collected(vid)
                if not is_collected:
                    cnt += 1
                    recorder.download_history_set(vid)

            logger.info(f"{len(vs)} in user {user} since {last_time}, {cnt} collected")
            recorder.set_last_collect_time(f"usr{user}")
