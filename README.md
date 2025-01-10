## How to set up the project

1. Choose one of the following options:
   - Download as ZIP: Click on the green "Code" button and select "Download ZIP". Extract the file to your desired location. 
   - Clone the project: Copy the cloning link (HTTPS). Open the terminal, navigate to your desired location, and run the command: ``git clone <cloning-link>``
2. Create and activate a virtual environment:
   - Windows:
      - Open the terminal and navigate to the project folder. Once there, create a virtual environment using the command: ``python -m venv .venv``
      - Activate the virtual environment using the command: ``.venv/Scripts/activate``. If using PowerShell, use the following command instead: ``.venv\Scripts\Activate.ps1``
   - Linux/macOS:
     - Open the terminal and navigate to the project folder. Once there, create a virtual environment using the command: ``python -m venv .venv``
     - Activate the virtual environment using the command: ``source .venv/bin/activate``
3. Install dependencies:
   - Navigate to the project folder in the terminal. Run the following command: ``pip install -r requirements.txt``
4. Place the config-file:
   - Place the given ``config.py`` file in the ``src`` directory. Make sure it is placed in the correct directory.

## How to run the project 

1. Make sure you have completed the steps in the "How to set up the project"-section.
2. Navigate to the project folder in the terminal.
3. Start the server by running the following command: ``uvicorn Main:app --port 8000``
4. Open any web browser and navigate to http://127.0.0.1:8000.
5. Select one of the world’s cuisines from the dropdown menu and click the Enter button.