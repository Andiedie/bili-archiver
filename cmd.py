import argparse

if __name__ == '__main__':
    parser = argparse.ArgumentParser(add_help=False, description='Bili Archiver')

    parser.add_argument('--help',
                        action='help')
    parser.add_argument('-s', '--session',
                        type=str, metavar='SESSDATA', help='bilibili cookie SESSDATA')
    parser.add_argument('-h', '--history',
                        action='store_true', default=True, help='include history')
    parser.add_argument('-f', '--self_favorite_folders',
                        action='store_true', default=True, help='include favorite folder')
    parser.add_argument('-u', '--user_ids',
                        type=int, nargs='*', metavar='0', help='user ids')

    args = parser.parse_args()

    print(args)
