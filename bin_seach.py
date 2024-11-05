import sys

def avg(l, r):
    return (l + r) / 2

if __name__ == '__main__':
    if len(sys.argv) != 3:
        print("usage:",sys.argv[0], "[left] [right]")
        sys.exit(1)

    left = float(sys.argv[1])
    right = float(sys.argv[2])

    average = avg(left, right)
    print("<",left,"|",average,"|",right,">")

    while (dir := input()):
        if dir == "l":
            right = average
        elif dir == "r":
            left = average
        else: 
            break

        average = avg(left, right)
        print("<",left,"|",average,"|",right,">")
