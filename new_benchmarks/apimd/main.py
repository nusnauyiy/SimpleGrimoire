from apimd.parser import test_one_input

def main():
    with open("test", "r") as f:
        inp = f.read()
        test_one_input(bytes(inp, "UTF-8"))

if __name__=="__main__":
    main()

