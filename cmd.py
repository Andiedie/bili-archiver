import argparse
from bili_archiver import collector, parser, downloader
from bili_archiver.api import BiliAPI
from bili_archiver.logger import logger
from pathlib import Path


if __name__ == '__main__':
    arg_parser = argparse.ArgumentParser(add_help=False, description='Bili Archiver')

    arg_parser.add_argument('--help',
                            action='help')
    arg_parser.add_argument('-c', '--cookies',
                            type=str, metavar='./bilibili.com_cookies', help='netscape http cookie file')
    arg_parser.add_argument('-h', '--history',
                            action='store_true', default=True, help='include history')
    arg_parser.add_argument('-f', '--self_favorite_folders',
                            action='store_true', default=True, help='include favorite folder')
    arg_parser.add_argument('-u', '--users',
                            action='store_true', default=True, help='include users in biliarchiver group')
    arg_parser.add_argument('-o', '--output',
                            type=str, metavar='.', help='output dir')

    args = arg_parser.parse_args()

    logger.info(f'running with args {args}')
    api = BiliAPI.from_file(Path(args.cookies))

    collector.collect(api, args.history, args.self_favorite_folders, args.users)
    downloader.download(api, Path(args.output))
