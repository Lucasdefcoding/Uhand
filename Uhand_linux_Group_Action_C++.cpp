#include <iostream>
#include <cstdint>
#include <cctype>

// Linux System Headers for Serial & Terminal Control
#include <fcntl.h>
#include <termios.h>
#include <unistd.h>
#include <sys/select.h>

const char* PORT = "/dev/ttyUSB1";
const speed_t BAUD = B9600;

int serial_fd = -1;
struct termios old_terminal_settings;

// Open and configure Linux serial port (/dev/ttyUSB1)
bool init_serial(const char* port_name) {
    serial_fd = open(port_name, O_RDWR | O_NOCTTY | O_NDELAY);
    if (serial_fd == -1) {
        std::cerr << "Error: Unable to open " << port_name << std::endl;
        return false;
    }

    // Clear flags for blocking read behavior configuration
    fcntl(serial_fd, F_SETFL, 0);

    struct termios options;
    tcgetattr(serial_fd, &options);

    // Set Baud Rate to 9600
    cfsetispeed(&options, BAUD);
    cfsetospeed(&options, BAUD);

    // 8N1 (8 Data bits, No parity, 1 Stop bit)
    options.c_cflag &= ~PARENB;
    options.c_cflag &= ~CSTOPB;
    options.c_cflag &= ~CSIZE;
    options.c_cflag |= CS8;

    // Enable receiver, local mode, disable hardware flow control
    options.c_cflag |= (CLOCAL | CREAD);
    options.c_cflag &= ~CRTSCTS;

    // Raw input/output mode (disable canonical processing, echo, signals)
    options.c_lflag &= ~(ICANON | ECHO | ECHOE | ISIG);
    options.c_oflag &= ~OPOST;

    tcsetattr(serial_fd, TCSANOW, &options);
    return true;
}

// Triggers a pre-saved action group stored in uHand flash memory
void run_action_group(uint8_t group_id, uint16_t times = 1) {
    uint8_t length = 5;
    uint8_t cmd = 0x06;  // CMD_ACTION_GROUP_RUN

    uint8_t times_low = times & 0xFF;
    uint8_t times_high = (times >> 8) & 0xFF;

    uint8_t packet[] = {
        0x55, 0x55,    // Header
        length,        // Length (5)
        cmd,           // Command (0x06)
        group_id,      // Action Group Number
        times_low,     // Repeat Count Low Byte
        times_high     // Repeat Count High Byte
    };

    write(serial_fd, packet, sizeof(packet));
    std::cout << "Triggered Action Group " << static_cast<int>(group_id) 
              << " (Repeat count: " << times << ")" << std::endl;
}

// Configures terminal into raw mode (non-blocking, no Enter key required)
void set_terminal_raw_mode() {
    tcgetattr(STDIN_FILENO, &old_terminal_settings);
    struct termios raw = old_terminal_settings;
    
    // Disable canonical mode & echo
    raw.c_lflag &= ~(ICANON | ECHO);
    tcsetattr(STDIN_FILENO, TCSANOW, &raw);
}

// Restores original terminal settings
void restore_terminal() {
    tcsetattr(STDIN_FILENO, TCSANOW, &old_terminal_settings);
}

// Non-blocking key listener equivalent to get_key_non_blocking()
char get_key_non_blocking() {
    fd_set set;
    struct timeval timeout;

    FD_ZERO(&set);
    FD_SET(STDIN_FILENO, &set);

    timeout.tv_sec = 0;
    timeout.tv_usec = 0;

    int res = select(STDIN_FILENO + 1, &set, NULL, NULL, &timeout);
    if (res > 0) {
        char c;
        if (read(STDIN_FILENO, &c, 1) > 0) {
            return c;
        }
    }
    return 0;
}

int main() {
    if (!init_serial(PORT)) {
        return 1;
    }

    std::cout << "Waiting 2 seconds for Arduino Nano reset..." << std::endl;
    sleep(2);

    std::cout << "\n--- uHand Instant Keyboard Control ---" << std::endl;
    std::cout << "Tap '0' through '5' to instantly run an action group movement." << std::endl;
    std::cout << "Press 'q' or ESC to exit.\n" << std::endl;

    set_terminal_raw_mode();

    while (true) {
        char key_char = get_key_non_blocking();

        if (key_char != 0) {
            key_char = std::tolower(key_char);

            // Exit program ('q' or ESC \x1b)
            if (key_char == 'q' || key_char == '\x1b') {
                std::cout << "\nExiting program." << std::endl;
                break;
            }

            // Check if key is a digit between '0' and '5'
            if (std::isdigit(key_char)) {
                int num = key_char - '0';
                if (num >= 0 && num <= 5) {
                    run_action_group(static_cast<uint8_t>(num));
                }
            }
        }

        usleep(10000); // 10ms loop delay (time.sleep(0.01))
    }

    // Cleanup resources
    restore_terminal();
    if (serial_fd != -1) {
        close(serial_fd);
    }

    return 0;
}