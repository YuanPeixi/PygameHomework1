def Find():
    s=input()
    s2=input()
    for c in s2:
        if s.find(c)==-1:
            print("FAILED")
            return
    print("FOUND")

if __name__=="__main__":
    Find()