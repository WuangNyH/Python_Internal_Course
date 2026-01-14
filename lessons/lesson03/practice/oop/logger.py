class Logger:
    @staticmethod
    def log(*args):
        if not args:
            print("No arguments")
            return
        # ghép tất cả args thành một chuỗi
        message = " ".join(str(x) for x in args)
        print("[LOG]", message)
