from typing import List
from bili_archiver import recorder
from bili_archiver.api import BiliAPI
from bili_archiver.logger import logger
from datetime import datetime


def collect(
        api: BiliAPI,
        from_history: bool = False,
        from_self_favorite_folders: bool = False,
        from_users: bool = False,
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

    if from_users:
        logger.info('collecting users from biliarchiver follow group')
        groups = [g for g in api.get_follow_groups() if g['name'] == 'biliarchiver']
        if len(groups) == 0:
            logger.warn('no follow group named biliarchiver')
            return

        users = {}
        for group in groups:
            logger.info(f"collecting users from follow group {group['name']}({group['tagid']})")
            for user in api.get_users_in_group(group['tagid']):
                users[user['mid']] = user

        for mid in users:
            logger.info(f"collecting videos from user {users[mid]['uname']}({mid})")
            last_time = recorder.get_last_collect_time(f"usr{mid}")
            vs = api.get_videos_of_user(mid, last_time)

            cnt = 0
            for v in vs:
                vid = v['id']
                is_collected = recorder.is_collected(vid)
                if not is_collected:
                    cnt += 1
                    recorder.download_history_set(vid)

            logger.info(f"{len(vs)} in user {users[mid]['uname']}({mid}) since {last_time}, {cnt} collected")
            recorder.set_last_collect_time(f"usr{mid}")
