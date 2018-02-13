#include <iostream>
#include <fstream.h>

using namespace std;

/*
*   this cpp file is used for saving
*   the output of file transmission
*   counter result via bluetooth from
*   the ev3 brick to the app
*/

int main(int total)
{
        ofstream SaveFile(“outputlogofbluetooth.txt”);
        SaveFile << total;
        SaveFile.close();
    return 0;
}
