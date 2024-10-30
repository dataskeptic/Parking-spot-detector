import threading
import cv2
import pickle
import numpy as np
import tkinter as tk
from tkinter import Button


image_path = r'C:\Users\mateu\Documents\Projects\trab-final-visao\trab-final-visao\carParkImg.png'

image_path = image_path.encode('utf-8').decode('utf-8')

try:
    with open('CarParkPos', 'rb') as f:
        posList = pickle.load(f)
except:
    posList = []


square_points = []


def mouseClick(events, x, y, flags, param):
    global square_points, posList

    if events == cv2.EVENT_LBUTTONDOWN:
        square_points.append((x, y))

        # Quando quatro pontos são clicados, adiciona o quadrado à lista
        if len(square_points) == 4:
            posList.append(tuple(square_points))
            square_points = []  # Reinicia a lista para o próximo quadrado
            with open('CarParkPos', 'wb') as f:
                pickle.dump(posList, f)

    elif events == cv2.EVENT_RBUTTONDOWN:
        # Verifica se o clique está dentro de algum quadrado para removê-lo
        for i, square in enumerate(posList):
            if point_in_polygon((x, y), square):
                posList.pop(i)
                break
        with open('CarParkPos', 'wb') as f:
            pickle.dump(posList, f)


def point_in_polygon(pt, poly):
    poly = np.array(poly)
    return cv2.pointPolygonTest(poly, pt, False) >= 0


def clear_positions():
    global posList
    posList = []
    with open('CarParkPos', 'wb') as f:
        pickle.dump(posList, f)


def update_image():
    while True:
        img = cv2.imread(image_path)
        if img is None:
            print(f"Erro: Não foi possível abrir a imagem {image_path}.")
            break


        for square in posList:
            pts = np.array(square, np.int32)
            pts = pts.reshape((-1, 1, 2))
            cv2.polylines(img, [pts], isClosed=True,
                          color=(255, 0, 0), thickness=2)


        for point in square_points:
            cv2.circle(img, point, 5, (0, 255, 0), -1)

        cv2.imshow("Image", img)
        cv2.setMouseCallback("Image", mouseClick)
        key = cv2.waitKey(1)
        if key == ord('f'):
            break

    cv2.destroyAllWindows()



root = tk.Tk()
root.title("Parking Space Picker")


clear_button = Button(root, text="Clear All", command=clear_positions)
clear_button.pack()


threading.Thread(target=update_image).start()


root.mainloop()
