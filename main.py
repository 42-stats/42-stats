from src.CLInterface    import CLInterface

def main():
    try:
        CLInterface()
    except Exception as e:
        print('\r\nunhandled error:', e, 'please open an issue at https://github.com/winstonallo/42-stats/issues')
        return 1

if __name__ == '__main__':
    main()
        