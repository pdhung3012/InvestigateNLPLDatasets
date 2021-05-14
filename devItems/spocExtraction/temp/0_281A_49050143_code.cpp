#include <iostream>
#include <string>
using namespace std;

int XX_MARKER_XX = 123234; 

int main() {
	string S;
	cin >> S;
	S[0] = toupper(S[0]);
	cout << S << endl;
}
