import argparse
from bili_archiver import collector, parser, downloader
from bili_archiver.api import BiliAPI
from bili_archiver.logger import logger


if __name__ == '__main__':
    arg_parser = argparse.ArgumentParser(add_help=False, description='Bili Archiver')

    arg_parser.add_argument('--help',
                            action='help')
    arg_parser.add_argument('-h', '--history',
                            action='store_true', default=True, help='include history')
    arg_parser.add_argument('-f', '--self_favorite_folders',
                            action='store_true', default=True, help='include favorite folder')
    arg_parser.add_argument('-u', '--user_ids',
                            type=int, nargs='*', metavar='0', help='user ids')

    args = arg_parser.parse_args()

    logger.info(f'running with args {args}')
    api = BiliAPI.from_env()

    collector.collect(args.history, args.self_favorite_folders, args.user_ids, api)
    videos = parser.parse(api)
    downloader.download(videos)
