import time
from threading import Thread
import random

import pyautogui
from PyQt5 import QtGui, uic
from PyQt5.QtWidgets import QApplication, QMainWindow
from PyQt5.QtCore import QObject, QThread, pyqtSignal, Qt

from .ChessBoard import ChessBoard
from .config import Config
from .ImageDetection import ImageDetection
from .MouseControl import MouseControl
from .StockfishManager import StockfishManager
from .logger import Logger
from pynput import keyboard






################################################################################################################
#
#
#
#
# Manager
#
#
#
#
################################################################################################################

class Manager(QObject):
    
    finished = pyqtSignal()
    stopped_bot = pyqtSignal()
    
    progress = pyqtSignal(int)
    show_image = pyqtSignal(str)
    write_label = pyqtSignal(str)
    auto_move_update = pyqtSignal()
    random_delay_update = pyqtSignal()
    slider_delay_update = pyqtSignal()
    slider_depth_update = pyqtSignal()
    slider_skill_update = pyqtSignal()
    board_found = pyqtSignal(bool)

    set_board_coordinates = pyqtSignal(list)
    set_field_height = pyqtSignal(int)
    set_field_width = pyqtSignal(int)
    set_board_height = pyqtSignal(int)
    set_board_width = pyqtSignal(int)


    path = "pictures/"
    turn_img = f"{path}turn_screen.png"
    game_running = True
    config = Config()
    bar_update_counter = 0
    moves_counter = 0
    auto_move = False
    random_delay = False
    first_move = True
    game_stopped = False
    opponent_Wrong_Turn_counter = 0
    myturn = False
    random_delay_max = 1
    depth_value = None
    skill_value = 0

    
    def __init__(self, parant, logger: Logger, auto_move = None, random_delay = None, board_coordinates = None, field_height = None, field_width = None, board_height = None, board_width = None):
        super(Manager, self).__init__()
        
        parant.stopped.connect(self.stopped)
        parant.automatic_move_change.connect(self.checkbox_change)
        parant.random_delay_change.connect(self.checkbox_randomdelay_change)
        parant.slider_delay_changed.connect(self.slider_delay_change)
        parant.slider_depth_changed.connect(self.slider_depth_change)
        parant.slider_skill_changed.connect(self.slider_skill_change)
        
        self.logger = logger
        self.board_coordinates = board_coordinates
        self.field_height = field_height
        self.field_width = field_width
        self.board_height = board_height
        self.board_width = board_width
        self.auto_move = auto_move
        self.random_delay = random_delay


    def run(self):
        
        screenshot = pyautogui.screenshot()
        screenshot.save(self.turn_img)
        imageDet = ImageDetection(self, self.logger)
        
        self.field_Cords, self.myturn = imageDet.calculate_field_cords(
            self.board_coordinates[0], self.field_height, self.field_width, self)
        chessBoard = ChessBoard()

        try:
            print(f"Depth Value: {self.depth_value}")
            print(f"Skill Level Value: {self.skill_value}")

            self.stockfish = StockfishManager(self.config.stockfish_path_name, self.skill_value)
        except Exception as e:
            self.logger.warning(f"Stockfish path wrong {e}")
            self.write_label.emit("Stockfish path \nwrong")
            self.game_stopped = True
        bot_move = "xxx"
        opponent_move = "xxx"
        tmp_skill = self.skill_value
        while self.game_running and not self.game_stopped:

            tmp_turn = self.myturn


            if tmp_skill != self.skill_value:
                self.stockfish.set_option("Skill Level", self.skill_value)
                tmp_skill = self.skill_value

            if chessBoard.getBoard().is_checkmate():
                self.game_running = False
                break
            if self.myturn:
                self.progress.emit(self.bar_update_counter)

                # bot_move = self.bot_Turn(self.stockfish, chessBoard, opponent_move)
                bot_move = self.bot_Turn(chessBoard, opponent_move)
            else:
                opponent_move = self.opponent_Turn(bot_move, chessBoard)
                if opponent_move == "NoneNone":
                    self.game_running = False
                    break
            
            if not tmp_turn == self.myturn and self.game_running:
                self.show_new_image(self.turn_img, imageDet)
                self.moves_counter += 1
            self.auto_move_update.emit()
            self.random_delay_update.emit()
            self.slider_delay_update.emit()
            self.slider_depth_update.emit()
            self.slider_skill_update.emit()
        if self.game_stopped:
            self.stopped_bot.emit()
        else:
            self.finished.emit()
    
    def show_new_image(self, path_name, imageDet):    
        screenshot = pyautogui.screenshot()
        screenshot.save(path_name)
        imageDet.saveResizedImag(path_name,
            self.board_coordinates[0][0], self.board_coordinates[0][1], self.board_coordinates[0][0]+self.board_width, self.board_coordinates[0][1]+self.board_height)
        self.update_image(path_name)
            

    def wait_before_move(self):
        if False == self.random_delay:
            return 0
        sampleList = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9,
                  10, 11, 12, 13, 14, 15, 16, 17, 18, 19,
                  20, 21, 22, 23, 24, 25, 26, 27, 28, 29,
                  30, 31, 32, 33, 34, 35, 36, 37, 38, 39,
                  40, 41, 42, 43, 44, 45, 46, 47, 48, 49,
                  50, 51, 52, 53, 54, 55, 56, 57, 58, 59,
                  60, 61, 62, 63, 64, 65, 66, 67, 68, 69,
                  70, 71, 72, 73, 74, 75, 76, 77, 78, 79,
                  80, 81, 82, 83, 84, 85, 86, 87, 88, 89,
                  90, 91, 92, 93, 94, 95, 96, 97, 98, 99]

        weights =    (100, 99, 98, 97, 96, 95, 94, 93, 92, 91,
                    10, 9, 8, 7, 6, 5, 4, 3, 2, 1,
                    5, 4, 4, 3, 3, 2, 2, 1, 1, 1,
                    0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                    0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                    0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                    0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                    0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                    0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                    0, 0, 0, 0, 0, 0, 0, 0, 0, 0)
        
        sampleList = [sampleList[x] for x in range(0, self.random_delay_max)]
        weights = [weights[x] for x in range(0, self.random_delay_max)]
    
        randomList = random.choices(
        sampleList, weights=weights, k=1)
        # print(randomList[0])
        # time.sleep(randomList[0])
        return randomList[0]
        
    # def bot_Turn(self, stockfish: StockfishManager, chessBoard, opponnentMove):
    def bot_Turn(self, chessBoard, opponnentMove):
        try:
            best_move = self.stockfish.get_best_move(chessBoard.getBoard(), self.depth_value)
        except Exception as e:
            self.logger.error(f"Failed to get stockfish best_move: {e}")
            
        if self.auto_move:
            self.first_move = True
            wait_time = self.wait_before_move()
            chessBoard.makeMove(best_move)
            self.write_label.emit(f"Bot move: {best_move}\nWait time: {wait_time}")
            if self.random_delay:
                time.sleep(wait_time)

            mouseContr = MouseControl()
            try:
                mouseContr.mousePos(
                    self.field_Cords[best_move[:2]][0], self.field_Cords[best_move[:2]][1])
                mouseContr.mouseClick()
                mouseContr.mousePos(
                    self.field_Cords[best_move[2:4]][0], self.field_Cords[best_move[2:4]][1])
                mouseContr.mouseClick()
            except Exception as e:
                self.logger.error(f"Mouse control failed: {e}")
                
            self.myturn = False
            return best_move
        else:
            
            if self.first_move:
                self.write_label.emit(f"Best move: {best_move}")
                imageDet = ImageDetection(self, self.logger)
                screenshot = pyautogui.screenshot()
                screenshot.save(self.turn_img)
                half_field_w = int(self.field_width/2)
                half_hield_h = int(self.field_height/2)
                imageDet.draw_rec_on_img(
                    self.turn_img,
                    self.field_Cords[best_move[:2]][0]-half_field_w,
                    self.field_Cords[best_move[:2]][1]-half_hield_h,
                    self.field_Cords[best_move[:2]][0]+half_field_w,
                    self.field_Cords[best_move[:2]][1]+half_hield_h)
                imageDet.draw_rec_on_img(
                    self.turn_img,
                    self.field_Cords[best_move[2:4]][0]-half_field_w,
                    self.field_Cords[best_move[2:4]][1]-half_hield_h,
                    self.field_Cords[best_move[2:4]][0]+half_field_w,
                    self.field_Cords[best_move[2:4]][1]+half_hield_h)
                imageDet.saveResizedImag(self.turn_img,
                    self.board_coordinates[0][0], self.board_coordinates[0][1], self.board_coordinates[0][0]+self.board_width, self.board_coordinates[0][1]+self.board_height)
                self.update_image(self.turn_img)
                self.first_move = False


            self.bar_update_counter += 2
            if self.bar_update_counter > 98:
                self.bar_update_counter = 2
                
            fmove, smove = self.detect_move()
            
            if fmove and smove and str(f"{fmove}{smove}") not in opponnentMove:
                if "1" in smove and chessBoard.getPiece(fmove) == "p":
                    smove = f"{smove}Q"
                try:
                    chessBoard.makeMove(f"{fmove}{smove}")
                    self.myturn = False
                    self.write_label.emit(f"Player move: \n{fmove}{smove}")
                    self.progress.emit(100)
                    self.bar_update_counter = 0
                    self.first_move = True
                    return str(f"{fmove}{smove}")
                except ValueError as e:
                    self.logger.warning(f"Something wrong with your move: {e}")
                

    def detect_move(self):
        screenshot = pyautogui.screenshot()
        screenshot.save(self.turn_img)
        imagDet = ImageDetection(self, self.logger)
        screen = imagDet.loadImag(self.turn_img)
        fmove = False
        smove = False
        color_counter = 0
        for field in self.field_Cords:
            
            x = self.field_Cords[field][0]
            y = self.field_Cords[field][1]
            x2 = int(x+(self.field_width/2)-5)
            y2 = int(y-(self.field_height/2)+10)

            if (screen[y2, x2][0] <= 115 and
                screen[y2, x2][1] >= 235 and
                    screen[y2, x2][2] >= 235):
                color_counter += 1
                yellow_white = [screen[y2, x2][0],
                                screen[y2, x2][1], screen[y2, x2][2]]
                if list(screen[y+int(self.field_height/2-13), x]) == yellow_white:
                    fmove = field
                else:
                    smove = field
            if (screen[y2, x2][0] <= 55 and
                screen[y2, x2][0] >= 34 and
                screen[y2, x2][1] <= 215 and
                screen[y2, x2][1] >= 193 and
                screen[y2, x2][2] <= 198 and
                screen[y2, x2][2] >= 177):
                color_counter += 1
                yellow_green = [screen[y2, x2][0],
                                screen[y2, x2][1], screen[y2, x2][2]]
                if list(screen[y+int(self.field_height/2-13), x]) == yellow_green:
                    fmove = field
                else:
                    smove = field
            
        if color_counter > 2:
            return False, False
        return fmove, smove
            
    def opponent_Turn(self, bot_move, chessBoard):
        if self.bar_update_counter == 0:
            self.write_label.emit(f"Waiting for\nOpponent move")
        self.bar_update_counter += 2
        if self.bar_update_counter > 98:
            self.bar_update_counter = 2
        self.progress.emit(self.bar_update_counter)
        
        fmove, smove = self.detect_move()

        if fmove and smove and str(f"{fmove}{smove}") not in bot_move:
            if "1" in smove and chessBoard.getPiece(fmove) == "p":
                smove = f"{smove}Q"
                
            try:
                chessBoard.makeMove(f"{fmove}{smove}")
                self.myturn = True
                self.write_label.emit(f"Opponent move: \n{fmove}{smove}")
                print(chessBoard.getBoard())
                self.progress.emit(100)
                self.bar_update_counter = 0
                return str(f"{fmove}{smove}")
            except ValueError as e:
                self.logger.warning(f"Something wrong with opponent move: {e}")
                if self.opponent_Wrong_Turn_counter < 101:
                    self.opponent_Wrong_Turn_counter += 1
                else:
                    self.opponent_Wrong_Turn_counter = 0
                    return str("NoneNone")

    def quick_detect_board(self):
        self.detect_board(quick_detect=True)

    def detect_board(self, quick_detect=False):
        screenshot = pyautogui.screenshot()
        screenshot.save(f"{self.path}screen.png")

        imageDet = ImageDetection(self, self.logger)

        try:
            boardFound, self.board_coordinates, self.field_height, self.field_width, self.board_height, self.board_width = imageDet.searchBoard(
                f"{self.path}screen.png", quick_detect)
            print(f"boardFound : {boardFound},\nself.board_coordinates : {self.board_coordinates}, \nself.field_height : {self.field_height}, self.field_width : {self.field_width}, \nself.board_height : {self.board_height}, self.board_width : {self.board_width}")
            self.set_board_coordinates.emit(self.board_coordinates)
            self.set_field_height.emit(self.field_height)
            self.set_field_width.emit(self.field_width)
            self.set_board_height.emit(self.board_height)
            self.set_board_width.emit(self.board_width)
        except Exception as e:
            boardFound = False
            self.logger.warning(f"Board not detected {e}")

        if not boardFound:
            self.write_label.emit("Board not detected\nmake sure that the\nchess board is visible\non your screen")
            self.board_found.emit(False)
        else:
            self.update_image("pictures/board_detection.png")
            self.board_found.emit(True)
            self.write_label.emit("")
        self.finished.emit()
            
    def update_bar(self, counter):
        self.progress.emit(counter)
    def update_image(self, img_path):
        self.show_image.emit(img_path)

    def checkbox_change(self, checked):
        if not self.auto_move == checked:
            self.bar_update_counter = 0
        self.auto_move = checked
    
    def checkbox_randomdelay_change(self, checked):
        self.random_delay = checked
    
    def slider_delay_change(self, value):
        if value < 1:
            value = 1
        self.random_delay_max = value
    
    def slider_depth_change(self, value):
        if value < 1:
            value = None
        self.depth_value = value
    
    def slider_skill_change(self, value):
        self.skill_value = value
        # self.stockfish.engine.configure({"Skill Level": value})
        
    def stopped(self):
        self.game_stopped = True
        self.stopped_bot.emit()








################################################################################################################
#
#
#
#
# GUI
#
#
#
#
################################################################################################################

class GUI(QMainWindow):

    stopped = pyqtSignal()
    automatic_move_change = pyqtSignal(bool)
    random_delay_change = pyqtSignal(bool)
    slider_delay_changed = pyqtSignal(int)
    slider_depth_changed = pyqtSignal(int)
    slider_skill_changed = pyqtSignal(int)
    listener = None

    def __init__(self):
        super(GUI, self).__init__()
        self.setWindowFlags(Qt.WindowStaysOnTopHint)

        self.logger = Logger()
        self.games_played = 0

        self.started = False
        uic.loadUi("gui/main.ui", self)

        self.show()
        self.set_label_text("")
        self.b_start.setEnabled(False)
        
        self.board_detected = False
        
        self.b_start.clicked.connect(self.start_bot)
        self.b_quit.clicked.connect(self.quit_programm)
        self.b_detect.clicked.connect(self.detect_board)
        self.b_quickDetect.clicked.connect(self.quick_detect_board)
        self.b_checkDetection.clicked.connect(self.check_detection)
        self.slider_delay.valueChanged.connect(self.slider_delay_change)
        self.slider_depth.valueChanged.connect(self.slider_depth_change)
        self.slider_skill.valueChanged.connect(self.slider_skill_change)
        
        self.logger.info(f"Init Main Window")

        self.listener = keyboard.Listener(on_press=self.on_press)
        self.listener.start()
        
    def on_press(self, key):
        try:
            k = key.char  # single-char keys
        except:
            k = key.name  # other keys
        if k in ['backspace']:  # keys of interest
            # self.keys.append(k)  # store it in global-like variable
            print('Key pressed: ' + k)
            if self.checkbox_automove_isChecked():
                self.box_automove.setChecked(False)
            else:
                self.box_automove.setChecked(True)
        elif k in ['\\']:
            print('Key pressed: ' + k)
            if self.checkbox_randomdelay_isChecked():
                self.box_randomdelay.setChecked(False)
            else:
                self.box_randomdelay.setChecked(True)
        elif k in ['m']:
            print('Key pressed: ' + k)
            if self.manager.myturn:
                self.manager.myturn = False
            else:
                self.manager.myturn = True
            print(f"self.manager.myturn : {self.manager.myturn}")
        elif k in ['f']:
            print('Key pressed: ' + k)
            if self.manager.first_move:
                self.manager.first_move = False
            else:
                self.manager.first_move = True
            print(f"self.manager.first_move : {self.manager.first_move}")
        else:
            # print('Key pressed: ' + k)
            pass

    def check_detection(self):
        if self.board_detected:
            self.clear_image()
            screenshot = pyautogui.screenshot()
            screenshot.save(f"pictures/check_detection.png")
            imageDet = ImageDetection(self, self.logger)
            imageDet.saveResizedImag(f"pictures/check_detection.png",
                                     self.boardCoordinates[0][0], self.boardCoordinates[0][1],
                                     self.boardCoordinates[0][0]+self.boardWidth, self.boardCoordinates[0][1]+self.boardHeight)
            self.show_image(f"pictures/check_detection.png")
            

        else:
            self.set_label_text("Detect Board first")
            
    def start_bot(self):
        
        if not self.started:
            self.logger.info(f"Started bot. Games played: {self.games_played}")
            print(f"Started bot. Games played: {self.games_played}")
            
            if self.games_played > 1:
                time.sleep(2)
            self.games_played += 1
            
            
            self.started = True
            self.set_label_text("")
            self.b_quickDetect.setEnabled(False)
            self.b_start.setText("Stop bot")
            self.b_detect.setEnabled(False)
            
            self.manager = Manager(self, self.logger, self.checkbox_automove_isChecked(), self.checkbox_randomdelay_isChecked(),
            self.boardCoordinates, self.fieldHeight, self.fieldWidth, self.boardHeight, self.boardWidth)
            self.thread = QThread()
            self.manager.moveToThread(self.thread)
            
            self.thread.started.connect(self.manager.run)
            self.manager.finished.connect(self.thread.quit)
            self.manager.stopped_bot.connect(self.thread.quit)
            
            self.manager.write_label.connect(self.set_label_text)
            self.manager.progress.connect(self.progressBarUpdate)
            self.manager.show_image.connect(self.show_image)
            self.manager.auto_move_update.connect(self.sent_checkbox_isChecked)
            self.manager.random_delay_update.connect(self.sent_checkbox_randomdelay_isChecked)
            self.manager.slider_delay_update.connect(self.slider_delay_change)
            self.manager.slider_depth_update.connect(self.slider_depth_change)
            self.manager.slider_skill_update.connect(self.slider_skill_change)

            self.slider_delay_change()
            self.slider_depth_change()
            self.slider_skill_change()
            
            self.delete_later()        
            self.thread.start()

            self.thread.finished.connect(
                lambda: self.set_label_text("")
            )
            self.manager.finished.connect(
                lambda: self.set_label_text("Game finished")
            )
            self.thread.finished.connect(
                lambda: self.b_quickDetect.setEnabled(True)
            )
            
            self.thread.finished.connect(
                lambda: self.b_start.setText("Start bot")
            )
            self.manager.stopped_bot.connect(
                lambda: self.show_image('pictures/board_detection.png')
            )
            self.at_finish()
            


        else:
            self.logger.info("Stop button pressed")
            self.started = False
            self.stopped.emit()
        
            
    def board_found(self, found):
        if found:
            self.b_start.setEnabled(True)
            self.board_detected = True
            self.label_board_found.setText("Board detected")
            self.label_board_found.setStyleSheet("color: green")
            self.b_checkDetection.setEnabled(True)
    
    def quick_detect_board(self):
        self.detect_board(quick_detect=True)

    def detect_board(self, quick_detect=False):

        self.b_detect.setEnabled(False)
        self.b_quickDetect.setEnabled(False)
        
        self.thread = QThread()
        self.manager = Manager(self, self.logger)
        self.manager.moveToThread(self.thread)

        if quick_detect:
            self.thread.started.connect(self.manager.quick_detect_board)
        else:
            self.thread.started.connect(self.manager.detect_board)
        
        self.manager.finished.connect(self.thread.quit)
        self.manager.progress.connect(self.progressBarUpdate)
        self.manager.write_label.connect(self.set_label_text)
        self.manager.show_image.connect(self.show_image)
        
        self.manager.set_board_coordinates.connect(self.set_boardCoordinates)
        self.manager.set_field_height.connect(self.set_fieldHeight)
        self.manager.set_field_width.connect(self.set_fieldWidth)
        self.manager.set_board_height.connect(self.set_boardHeight)
        self.manager.set_board_width.connect(self.set_boardWidth)
        self.manager.board_found.connect(self.board_found)
        
        self.delete_later()
        
        self.thread.start()
        
        self.at_finish()

    def at_finish(self):
        self.thread.finished.connect(
            lambda: self.progressBarUpdate(0)
        )
        self.thread.finished.connect(
            lambda: self.b_detect.setEnabled(True)
        )
        self.thread.finished.connect(
            lambda: self.b_quickDetect.setEnabled(True)
        )
        self.started = False
        
    def slider_delay_change(self):
        delay_value = self.slider_delay.value()
        if delay_value > 0:
            delay_value = delay_value - 1 
        self.label_random_delay.setText(f"Delay ({delay_value}):")
        # print(f"Delay: {delay_value} sec")
        self.slider_delay_changed.emit(self.slider_delay.value())
    
    def slider_depth_change(self):
        depth_value = self.slider_depth.value()
        self.label_depth.setText(f"Depth ({depth_value}):")
        self.slider_depth_changed.emit(self.slider_depth.value())
    
    def slider_skill_change(self):
        skill_value = self.slider_skill.value()
        self.label_skill.setText(f"Skills ({skill_value}):")
        self.slider_skill_changed.emit(self.slider_skill.value())
        
        
        
    def delete_later(self):
        self.manager.finished.connect(self.manager.deleteLater)
        self.manager.progress.connect(self.manager.deleteLater)
        self.manager.write_label.connect(self.manager.deleteLater)
        self.manager.show_image.connect(self.manager.deleteLater)
        self.thread.finished.connect(self.thread.deleteLater)
        

    def set_boardCoordinates(self, board_coordinates):
        self.boardCoordinates = board_coordinates
    def set_fieldHeight(self, field_h):
        self.fieldHeight = field_h
    def set_fieldWidth(self, field_w):
        self.fieldWidth = field_w
    def set_boardHeight(self, board_h):
        self.boardHeight = board_h
    def set_boardWidth(self, board_w):
        self.boardWidth = board_w

    def show_settings(self):
        pass
        #TODO

    def quit_programm(self):
        if self.listener is not None:
            self.listener.stop()
        exit()

    def show_image(self, img_path):
        try:
            pixmap = QtGui.QPixmap(img_path)
            pixmap = pixmap.scaled(521, 521)
            self.label_image.setPixmap(pixmap)
            self.label_image.show()
        except Exception:
            self.logger.error("Error displaying image in QLabel=label_image: {e}")

    def clear_image(self):
        self.label_image.clear()
    
    def sent_checkbox_isChecked(self):
        self.automatic_move_change.emit(self.checkbox_automove_isChecked())

    def checkbox_automove_isChecked(self):
        return self.box_automove.isChecked()

    def sent_checkbox_randomdelay_isChecked(self):
        self.random_delay_change.emit(self.checkbox_randomdelay_isChecked())

    def checkbox_randomdelay_isChecked(self):
        return self.box_randomdelay.isChecked()

    def progressBarUpdate(self, value):
        self.progressBar.setValue(value)

    def set_label_text(self, text):
        self.label_text.setText(text)






def main():
    try:
        app = QApplication([])
        window = GUI()
        app.exec_()
    except Exception as e:
        print(e)

    


