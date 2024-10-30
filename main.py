import cv2
import pickle
import cvzone
import numpy as np

# cap = cv2.VideoCapture('video_internet.mp4')
#cap = cv2.VideoCapture('video_estacionamento.mp4')
cap = cv2.VideoCapture('carPark.mp4')

with open('CarParkPos', 'rb') as f:
    posList = pickle.load(f)

def checkParkingSpace(imgPro, img):
    spaceCounter = 0
    for square in posList:
        if len(square) == 4:
            pts = np.array(square, np.int32)
            rect = cv2.boundingRect(pts)
            x, y, w, h = rect

            imgCrop = imgPro[y:y+h, x:x+w]

            # Detecta contornos na imagem recortada
            contours, _ = cv2.findContours(imgCrop, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            # CONTA OS CONTORNOS DETECTADOS
            count = len(contours)
            cvzone.putTextRect(img, str(count), (x, y+h-2), scale=1, thickness=2,
                               offset=0, colorT=(255, 255, 255), colorR=(0, 0, 255))

            if count < 7:  # Ajuste aqui para diminuir a sensibilidade
                color = (0, 255, 0)
                thickness = 2
                spaceCounter += 1
            else:
                color = (0, 0, 255)
                thickness = 2

            cv2.rectangle(img, (x, y), (x + w, y + h), color, thickness)

    cvzone.putTextRect(img, f'Available spots : {spaceCounter}/{len(posList)}',
                       (50, 50), scale=2, thickness=1, offset=2, colorR=(0, 0, 0))

while True:
    if cap.get(cv2.CAP_PROP_POS_FRAMES) == cap.get(cv2.CAP_PROP_FRAME_COUNT):
        cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
    success, img = cap.read()

    if not success:
        print("Erro: Não foi possível ler o quadro do vídeo.")
        break

    # CONVERTE IMAGEM PRA CINZA
    imgGray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    # REDUZ O RUÍDO
    imgBlur = cv2.GaussianBlur(imgGray, (5, 5), 1)

    # converte a imagem para binário
    imgThreshold = cv2.adaptiveThreshold(
        imgBlur, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV, 25, 16)

    # remove o ruído
    imgMedian = cv2.medianBlur(imgThreshold, 5)

    # DILATAÇÃO DAS BORDAS
    kernel = np.ones((3, 3), np.uint8)
    imgDilate = cv2.dilate(imgMedian, kernel, iterations=1)

    # Opções adicionais de filtro morfológico
    imgErode = cv2.erode(imgDilate, kernel, iterations=1)

    checkParkingSpace(imgErode, img)

    cv2.imshow("Image", img)
   # cv2.imshow("Gray", imgGray)
   # cv2.imshow("Blur", imgBlur)
   # cv2.imshow("Threshold", imgThreshold)
   # cv2.imshow("Median", imgMedian)
   # cv2.imshow("Dilate", imgDilate)


    key = cv2.waitKey(1)
    if key == ord('f'):
        break

cv2.destroyAllWindows()
