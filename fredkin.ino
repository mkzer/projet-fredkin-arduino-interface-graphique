#include <MCUFRIEND_kbv.h>

MCUFRIEND_kbv tft;

// Couleurs 16 bits (RGB565)
#define WHITE 0xFFFF
#define BLACK 0x0000
#define RED   0xF800

// Dimensions fixes : 48x32
#define WIDTH 48
#define HEIGHT 32
#define CELL_SIZE 10  // Sur un écran 480×320
#define SERIAL_TIMEOUT 1000  // Timeout en millisecondes

// Buffer partagé pour les deux règles Fredkin
uint8_t grid[WIDTH][HEIGHT];
uint8_t* sharedBuffer = nullptr;  // Buffer temporaire pour les calculs
int generations = 0;

// État de la simulation
bool simulationRunning = false;
unsigned long lastSerialCheck = 0;

void setup() {
    Serial.begin(115200);
    
    // Initialisation de l'écran
    uint16_t ID = tft.readID();
    if (ID == 0xD3D3) ID = 0x9486; // Ajustement pour certains écrans
    tft.begin(ID);
    tft.setRotation(1);   // orientation paysage
    tft.fillScreen(WHITE);
    
    // Allocation du buffer partagé
    sharedBuffer = new uint8_t[WIDTH * HEIGHT];
    
    // Message de démarrage
    Serial.println("LOG,System started");
}

void loop() {
    // Vérifie les commandes série avec timeout
    if (Serial.available()) {
        String command = Serial.readStringUntil('\n');
        processCommand(command);
    }
}

void processCommand(const String &command) {
    if (command.startsWith("GEN:")) {
        parseGenCommand(command);
    }
    else if (command == "MODE:FREDKIN1") {
        if (!simulationRunning) {
            runSimulationFredkin1();
        }
    }
    else if (command == "MODE:FREDKIN2") {
        if (!simulationRunning) {
            runSimulationFredkin2();
        }
    }
}

bool waitForAck(unsigned long timeout = SERIAL_TIMEOUT) {
    unsigned long startTime = millis();
    while (!Serial.available()) {
        if (millis() - startTime > timeout) {
            return false;
        }
    }
    String ack = Serial.readStringUntil('\n');
    return ack == "OK";
}

void parseGenCommand(const String &cmd) {
    int pos1 = cmd.indexOf(':');
    int pos2 = cmd.indexOf(':', pos1 + 1);
    
    if (pos1 < 0 || pos2 < 0) {
        Serial.println("LOG,Error: Invalid command format");
        return;
    }
    
    String genStr = cmd.substring(pos1 + 1, pos2);
    generations = genStr.toInt();
    
    if (generations <= 0) {
        Serial.println("LOG,Error: Invalid generation count");
        return;
    }
    
    String bits = cmd.substring(pos2 + 1);
    if (bits.length() != WIDTH * HEIGHT) {
        Serial.println("LOG,Error: Invalid grid data length");
        return;
    }
    
    // Remplir la grille
    int idx = 0;
    for (int y = 0; y < HEIGHT; y++) {
        for (int x = 0; x < WIDTH; x++) {
            grid[x][y] = (bits.charAt(idx++) == '1') ? 1 : 0;
        }
    }
    
    drawGrid();
    Serial.println("LOG,Grid initialized");
}

void drawGrid() {
    tft.fillScreen(WHITE);
    
    for (int y = 0; y < HEIGHT; y++) {
        for (int x = 0; x < WIDTH; x++) {
            uint16_t color = (grid[x][y] == 1) ? RED : WHITE;
            tft.fillRect(x * CELL_SIZE, y * CELL_SIZE, CELL_SIZE, CELL_SIZE, color);
            tft.drawRect(x * CELL_SIZE, y * CELL_SIZE, CELL_SIZE, CELL_SIZE, BLACK);
        }
    }
}

void runSimulationFredkin1() {
    simulationRunning = true;
    
    for (int g = 1; g <= generations; g++) {
        if (!evolveFredkin1()) {
            Serial.println("LOG,Error: Simulation interrupted");
            break;
        }
        
        drawGrid();
        
        // Stats
        int aliveCount = countAliveCells();
        int deadCount = (WIDTH * HEIGHT) - aliveCount;
        
        // Log principal
        Serial.print("LOG,FREDKIN1,GEN:");
        Serial.print(g);
        Serial.print(",ALIVE:");
        Serial.print(aliveCount);
        Serial.print(",DEAD:");
        Serial.println(deadCount);
        
        // Grille
        sendGridState();
        
        // Attendre acknowledgement avec timeout
        if (!waitForAck()) {
            Serial.println("LOG,Error: Ack timeout");
            break;
        }
    }
    
    simulationRunning = false;
}

bool evolveFredkin1() {
    if (!sharedBuffer) return false;
    
    for (int y = 0; y < HEIGHT; y++) {
        for (int x = 0; x < WIDTH; x++) {
            int sumNeighbors = 0;
            
            // Voisins orthogonaux
            if (y > 0) sumNeighbors += grid[x][y - 1];
            if (y < HEIGHT - 1) sumNeighbors += grid[x][y + 1];
            if (x > 0) sumNeighbors += grid[x - 1][y];
            if (x < WIDTH - 1) sumNeighbors += grid[x + 1][y];
            
            sharedBuffer[y * WIDTH + x] = (sumNeighbors % 2);
        }
    }
    
    // Copie du buffer vers la grille
    for (int y = 0; y < HEIGHT; y++) {
        for (int x = 0; x < WIDTH; x++) {
            grid[x][y] = sharedBuffer[y * WIDTH + x];
        }
    }
    
    return true;
}

void runSimulationFredkin2() {
    simulationRunning = true;
    
    for (int g = 1; g <= generations; g++) {
        if (!evolveFredkin2()) {
            Serial.println("LOG,Error: Simulation interrupted");
            break;
        }
        
        drawGrid();
        
        // Stats
        int aliveCount = countAliveCells();
        int deadCount = (WIDTH * HEIGHT) - aliveCount;
        
        // Log principal
        Serial.print("LOG,FREDKIN2,GEN:");
        Serial.print(g);
        Serial.print(",ALIVE:");
        Serial.print(aliveCount);
        Serial.print(",DEAD:");
        Serial.println(deadCount);
        
        // Grille
        sendGridState();
        
        // Attendre acknowledgement avec timeout
        if (!waitForAck()) {
            Serial.println("LOG,Error: Ack timeout");
            break;
        }
    }
    
    simulationRunning = false;
}

bool evolveFredkin2() {
    if (!sharedBuffer) return false;
    
    const int8_t offsets[8][2] = {
        {-1,-1}, {0,-1}, {1,-1},
        {-1, 0},         {1, 0},
        {-1, 1}, {0, 1}, {1, 1}
    };
    
    for (int y = 0; y < HEIGHT; y++) {
        for (int x = 0; x < WIDTH; x++) {
            int sum = 0;
            // Vérification des 8 voisins
            for (int i = 0; i < 8; i++) {
                int nx = x + offsets[i][0];
                int ny = y + offsets[i][1];
                if (nx >= 0 && nx < WIDTH && ny >= 0 && ny < HEIGHT) {
                    sum += grid[nx][ny];
                }
            }
            sharedBuffer[y * WIDTH + x] = sum % 2;
        }
    }
    
    // Copie du buffer vers la grille
    for (int y = 0; y < HEIGHT; y++) {
        for (int x = 0; x < WIDTH; x++) {
            grid[x][y] = sharedBuffer[y * WIDTH + x];
        }
    }
    
    return true;
}

int countAliveCells() {
    int count = 0;
    for (int y = 0; y < HEIGHT; y++) {
        for (int x = 0; x < WIDTH; x++) {
            if (grid[x][y] == 1) count++;
        }
    }
    return count;
}

void sendGridState() {
    for (int y = 0; y < HEIGHT; y++) {
        for (int x = 0; x < WIDTH; x++) {
            Serial.print(grid[x][y]);
        }
        Serial.println();
    }
}

void cleanup() {
    if (sharedBuffer) {
        delete[] sharedBuffer;
        sharedBuffer = nullptr;
    }
}
