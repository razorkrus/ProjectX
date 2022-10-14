import logging


def main():
    logging.basicConfig(level=logging.DEBUG,
                        format='[%(levelname)-7s @ %(asctime)s] %(message)s',
                        datefmt='%Y/%m/%d %H:%M:%S')


if __name__ == '__main__':
    main()
