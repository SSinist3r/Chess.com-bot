import sys
if sys.version_info[0] < 3:
    raise Exception(
        "Must be using Python version 3. Developed with Python 3.8.8")
if sys.version_info[1] != 8:
    print("WARNING: Developed with Python version 3.8.8. May not work properly if used with another version")
elif sys.version_info[2] != 8:
    print("WARNING: Developed with Python version 3.8.8. May not work properly if used with another version")
