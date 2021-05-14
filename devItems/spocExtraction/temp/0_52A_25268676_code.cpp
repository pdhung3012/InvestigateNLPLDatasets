using namespace std;

int main() {
	int n;
	cin >> n;
	int freq[3] = {};
	for (int i = 0; i < n; i++) {
		int x;
		cin >> x;
		freq[x - 1]++;
	}
	int m = max(freq[0], max(freq[1], freq[2]));
	cout << n - m << endl;
}