#include <iostream>
#include <fstream.h>
#include "string.h"

using namespace std;

/*
*   this cpp file is used for saving
*   the output of file log
*   result via bluetooth from
*   the ev3 brick to the app
*/

int main(string log)
{
        ofstream SaveFile(“outputlogofbluetooth.txt”);
        SaveFile << log;
        SaveFile.close();
    return 0;
}
