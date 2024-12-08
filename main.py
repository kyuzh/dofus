import pyautogui
from pywinauto import Application, findwindows, keyboard
import time
from pynput.mouse import Listener,Button, Controller
from pynput.keyboard import Controller
import numpy as np
import cv2
import keyboard

from matplotlib import pyplot as plt



# This function will capture the position when mouse is pressed
def on_click(x, y, button, pressed):
    global start_x, start_y, end_x, end_y

    if pressed:
        # Store the initial click position
        start_x, start_y = x, y
        print(f"Selection started at ({start_x}, {start_y})")
    else:
        # Store the position where the mouse is released
        end_x, end_y = x, y
        print(f"Selection ended at ({end_x}, {end_y})")

        # Stop the listener after the mouse is released
        return False


def select_area():
    global start_x, start_y, end_x, end_y
    start_x = start_y = end_x = end_y = None

    # Create a listener for mouse events
    with Listener(on_click=on_click) as listener:
        print("Click and drag the mouse to select a region of the screen.")
        listener.join()

    # Once mouse selection is done, return the coordinates
    if start_x and start_y and end_x and end_y:
        print(f"Region selected: Start({start_x}, {start_y}) to End({end_x}, {end_y})")
        return (start_x, start_y, end_x, end_y)
    else:
        print("No region selected.")
        return None



def find_image_on_screen(image_path, confidence=0.8):
    """
    Recherche une image spécifique dans la capture d'écran et retourne
    les coordonnées du centre de l'image si elle est trouvée.

    Args:
        image_path (str): Le chemin de l'image à rechercher dans la capture d'écran.

    Returns:
        tuple: Les coordonnées du centre de l'image (x, y) ou None si l'image n'est pas trouvée.
    """
    try:
        # Rechercher l'image dans l'écran
        location = pyautogui.locateOnScreen(image_path, confidence=confidence)

        if location:
            # Si l'image est trouvée, obtenir les coordonnées du centre
            center = pyautogui.center(location)
            return center
        else:
            print("Image non trouvée.")
            return None
    except pyautogui.ImageNotFoundException:
        print("Erreur : Image non trouvée.")
        return None

def capture_full_screen():
    """
    Take a full-screen screenshot and return it as a numpy array.
    """
    screenshot = pyautogui.screenshot()
    screenshot_np = np.array(screenshot)
    # Convert from RGB to BGR for OpenCV
    screenshot_bgr = cv2.cvtColor(screenshot_np, cv2.COLOR_RGB2BGR)
    return screenshot_bgr


def compare_images_and_find_differences(img1, img2):
    """
    Compare two full-screen images, highlight the differences with rectangles, and display the results.

    Args:
        img1 (numpy array): First image to compare.
        img2 (numpy array): Second image to compare.

    Returns:
        List of bounding boxes for regions with significant differences.
    """
    # Compute the absolute difference between the two images
    difference = cv2.absdiff(img1, img2)

    # Convert the difference image to grayscale
    gray_diff = cv2.cvtColor(difference, cv2.COLOR_BGR2GRAY)

    # Apply thresholding to highlight significant differences
    _, thresh_diff = cv2.threshold(gray_diff, 30, 255, cv2.THRESH_BINARY)

    # Find contours (connected components) in the thresholded image
    contours, _ = cv2.findContours(thresh_diff, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    # List to store bounding boxes of areas with significant differences
    diff_regions = []

    # Draw bounding boxes around detected differences
    img_with_rects = img1.copy()
    for contour in contours:
        if cv2.contourArea(contour) > 500:  # Only consider large differences (area > 500 pixels)
            # Get bounding box for each contour
            x, y, w, h = cv2.boundingRect(contour)
            diff_regions.append((x, y, w, h))  # Store bounding box coordinates

            # Draw rectangle on the copy of the first image
            cv2.rectangle(img_with_rects, (x, y), (x + w, y + h), (0, 255, 0), 2)  # Green rectangle

    # Display the images and the difference
    '''
    plt.figure(figsize=(15, 5))
    plt.subplot(1, 4, 1), plt.imshow(cv2.cvtColor(img1, cv2.COLOR_BGR2RGB)), plt.title('Image 1')
    plt.subplot(1, 4, 2), plt.imshow(cv2.cvtColor(img2, cv2.COLOR_BGR2RGB)), plt.title('Image 2')
    plt.subplot(1, 4, 3), plt.imshow(thresh_diff, cmap='gray'), plt.title('Difference')
    plt.subplot(1, 4, 4), plt.imshow(cv2.cvtColor(img_with_rects, cv2.COLOR_BGR2RGB)), plt.title('Detected Differences')
    plt.tight_layout()
    plt.show()
    '''
    return diff_regions


def scan_zones_with_mouse(zones, step=20, delay=0.01, stop_key='esc'):
    """
    Déplace la souris à travers les zones spécifiées avec un pas donné, avec une option d'arrêt.

    Args:
        zones (list of tuples): Liste des rectangles définis par (x, y, w, h).
        step (int): Pas du balayage en pixels.
        delay (float): Délai en secondes entre chaque mouvement de la souris.
        stop_key (str): Touche pour arrêter le balayage (par défaut 'esc').
    """
    print(f"Appuyez sur '{stop_key}' pour arrêter le balayage à tout moment.")
    for zone in zones:
        x, y, w, h = zone

        # Parcourir la zone en se déplaçant selon le pas
        for i in range(y, y + h, step):
            for j in range(x, x + w, step):
                # Vérifier si la touche d'arrêt est pressée
                if keyboard.is_pressed(stop_key):
                    print("Balayage interrompu par l'utilisateur.")
                    return
                pyautogui.moveTo(j, i)
                time.sleep(0.2)

                job_xp = find_image_on_screen(r"C:\Users\manji\dofus\pythonProject1\image\job_xp.png", confidence=0.5)
                if not job_xp:
                    continue
                job_epuise = find_image_on_screen(r"C:\Users\manji\dofus\pythonProject1\image\job_epuise.png", confidence=0.8)
                if job_xp and not job_epuise:
                    # Déplacer la souris
                    pyautogui.moveTo(j, i)
                    pyautogui.mouseDown()
                    time.sleep(0.03)
                    # Relâcher le clic (mouse up)
                    pyautogui.mouseUp()
                    time.sleep(delay)

        # Revenir au coin supérieur gauche de la zone après le balayage
        pyautogui.moveTo(x, y)

    print("Balayage terminé.")


pyautogui.FAILSAFE = False  # Désactive le fail-safe

# List all open windows
windows = findwindows.find_elements()
for window in windows:
    print(f"Title: {window.name}, Class: {window.class_name}, Handle: {window.handle}")

name_window = "Kyuzh - Sacrieur - 3.0.14.10*"
# Attempt to connect to a specific Microsoft Edge window
app = Application(backend="win32").connect(
    title_re=name_window)
main_window = app.window(title_re=name_window)
main_window.set_focus()



time.sleep(1)

# Capture the first image
image1 = capture_full_screen()
keyboard_controller = Controller()

# Simuler un appui sur la touche 'a'
keyboard_controller.press('y')

# Attendre un moment (optionnel)
time.sleep(1)

image2 = capture_full_screen()

# Attendre pendant la durée spécifiée
time.sleep(0.5)

# Relâcher la touche 'a'
keyboard_controller.release('y')
# Compare the two images
# Compare the two images and get the regions with the most significant differences
diff_regions = compare_images_and_find_differences(image1, image2)


# Afficher les zones détectées
print("Zones avec différences significatives :", diff_regions)
while True:
    scan_zones_with_mouse(diff_regions[0:-2], step=50, delay=1, stop_key='esc')
    if keyboard.is_pressed('esc'):
        print("Balayage interrompu par l'utilisateur.")
        break