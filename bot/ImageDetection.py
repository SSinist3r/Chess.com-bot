import cv2 as cv



class ImageDetection:
    boardFound = False
    board_coordinates = None
    field_height = None
    field_width = None
    board_height = None
    board_width = None
    def __init__(self, manager, logger):
        self.manager = manager
        self.logger = logger

    def searchBoard(self, screenshot_path, quick_detect=False):
        if quick_detect:
            print("Board found : Using Quick Detect")
            return True, [(237, 163), (334, 260)], 97.75, 97.875, 782, 783
        try:
            self.boardFound, self.board_coordinates, self.field_height, self.field_width, self.board_height, self.board_width = self.searchBoardWithClr(screenshot_path, "pictures/layout1.PNG")
        except Exception:
            pass
        if self.boardFound:
            print("Board found : WHITE")
            return self.boardFound, self.board_coordinates, self.field_height, self.field_width, self.board_height, self.board_width
        else:
            try:
                self.boardFound, self.board_coordinates, self.field_height, self.field_width, self.board_height, self.board_width = self.searchBoardWithClr(screenshot_path, "pictures/layout2.PNG")
            except Exception:
                pass
            if self.boardFound:
                print("Board found : BLACK")
                return self.boardFound, self.board_coordinates, self.field_height, self.field_width, self.board_height, self.board_width
            else:
                print("Board not found > Providing Testing Location")
                # return False, None, None, None, None, None
                return True, [(237, 163), (334, 260)], 97.75, 97.875, 782, 783
                
    def searchBoardWithClr(self, screenshot_path, board_layout_path):
        """
        Search board on screen, rescale if not found (100x times)

        Returns:
            [[(int),(int)], int, int , int, int]: Boad coordinates left, upper corner and right lower corner x and y,
                                                single field height, single field width, board height, board width
        """
        screenshot = cv.imread(screenshot_path, cv.IMREAD_UNCHANGED)
        board_layout1 = cv.imread(board_layout_path)

        maxValue1 = 0
        #dots = "."
        threshold = 0.9
        print("Searching board", end="\r")
        for c in range(100):
            self.manager.update_bar(c)
            #print(f"Searching board {dots*c}", end="\r")
            board_result1 = cv.matchTemplate(
                screenshot, board_layout1, cv.TM_CCOEFF_NORMED)

            _, max_val1, _, max_loc1 = cv.minMaxLoc(
                board_result1)
            if max_val1 > maxValue1:
                maxValue1 = max_val1
                maxLoc1 = max_loc1
                board_w1 = board_layout1.shape[1]
                board_h1 = board_layout1.shape[0]
            width1 = int(board_layout1.shape[1] * 99/100)
            higth1 = int(board_layout1.shape[0] * 99/100)
            board_layout1 = cv.resize(board_layout1, (width1, higth1))
            if maxValue1 >= threshold:
                self.logger.info(f"Board detected")
                cv.imwrite("pictures/board_detection.png",
                           screenshot[maxLoc1[1]:int(maxLoc1[1]+board_h1), maxLoc1[0]:int(maxLoc1[0]+board_w1)])
                self.manager.update_image("pictures/board_detection.png")
                return True, [maxLoc1, (int(maxLoc1[0]+board_w1/8), int(maxLoc1[1]+board_h1/8))], board_h1/8, board_w1/8,  board_h1, board_w1


    def calculate_field_cords(self, top_left, field_h, field_w, manager):
        
        screenimg = cv.imread("pictures/turn_screen.png", cv.IMREAD_UNCHANGED)
        bottom_right = (int(top_left[0]+field_w), int(top_left[1]+field_h))
        start_X = top_left[0]
        start_Y = top_left[1]
        firstX = True
        firstY = True
        fields_Cords = {}
        abc = "abcdefgh"
        oneTwothree = "87654321"
        myturn = True
        #cv.circle(
        #    screenimg, (start_X+int(field_w/2), top_left[1]+int(field_h/2)), 5, color=(35, 120, 255))
        #cv.imwrite("test.png", screenimg)
        try:
            if screenimg[top_left[1]+int(field_h/2), start_X+int(field_w/2)][0] > 200 and screenimg[top_left[1]+int(field_h/2), start_X+int(field_w/2)][1] > 200 and screenimg[top_left[1]+int(field_h/2), start_X+int(field_w/2)][2] > 200:
                oneTwothree = "12345678"
                abc = "hgfedcba"
                myturn = False
        except IndexError as e:
            self.logger.error(f"INDEXERROR: {e}.\ntop_left[1]={top_left[1]}\nfield_h/2={field_h/2}\nstart_X={start_X}\nfield_w/2={field_w/2}")
            raise e
        for c in range(8):
            firstX = True
            if not firstY:
                tmp = list(top_left)
                tmp[1] = int(tmp[1]+field_h)
                tmp[0] = int(start_X)
                top_left = tuple(tmp)
            else:
                firstY = False
            for c1 in range(8):
                if not firstX:
                    tmp = list(top_left)
                    tmp[0] = int(tmp[0]+field_w)
                    top_left = tuple(tmp)
                    bottom_right = (
                        int(top_left[0]+field_w), int(top_left[1]+field_h))

                else:
                    firstX = False
                #fields_Cords.append([int(top_left[0] + ( field_w / 2 )), int( top_left[1] + ( field_h / 2 ))])
                fields_Cords.update(
                    {str(abc[c1]+oneTwothree[c]): [int(top_left[0] + (field_w / 2)), int(top_left[1] + (field_h / 2))]})
                cv.rectangle(screenimg, top_left, bottom_right, color=(
                    0, 255, 0), thickness=2, lineType=cv.LINE_4)

        for key, c in fields_Cords.items():
            #print(key, c)
            cv.circle(screenimg, tuple(c), 5, color=(0, 0, 255))
            cv.putText(screenimg, str(key), tuple(
                c), cv.FONT_HERSHEY_SIMPLEX, fontScale=1, thickness=2, color=(142, 142, 142))
        #cv.imshow('Result', screenimg)
        #cv.imwrite("pictures/board_result.jpg", screenimg)
        #screenimg = cv.imread("pictures/board_result.jpg")
        cv.imwrite("pictures/board_detection.png",
                   screenimg[start_Y:int(start_Y+(field_h*8)), start_X:int(start_X+(field_w*8))])
        manager.update_image("pictures/board_detection.png")
        return fields_Cords, myturn

    def saveResizedImag(self, img_path, x1, y1, x2, y2):
        img = cv.imread(img_path)
        cv.imwrite(img_path,
                   img[y1:y2, x1:x2])

    def loadImag(self, img_path):
        return cv.imread(img_path)

    def draw_circle_on_img(self, img_path, x, y):
        img = cv.imread(img_path)
        cv.circle(img, (x, y), 5, color=(0, 0, 255))
        cv.imwrite(img_path, img)
        
    def draw_rec_on_img(self, img_path, x1, y1, x2, y2):
        img = cv.imread(img_path)
        cv.rectangle(img, (x1, y1), (x2, y2), color=(
        0, 0, 255), thickness=2, lineType=cv.LINE_4)
        cv.imwrite(img_path, img)
