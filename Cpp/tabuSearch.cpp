#include <iostream>     
#include <fstream> 
#include <sstream>
#include <vector>
#include <limits>
#include <ctime>
#include <algorithm>
#include <filesystem>
#include <unordered_set>
#include <functional>
#include <numeric>

struct algorithmResult{
    int time;
    double cost;
    std::vector<int> path;
};

algorithmResult tabuSearch(std::vector<std::vector<double>> graqphMatrix);

int main(int argc, char *argv[]){
    std::vector<std::vector<double>> graphMatrix;

    if (!std::filesystem::exists("testInstance")) {
        std::filesystem::create_directory("testInstance");
    }

    std::ifstream file("testInstance/" + std::string(argv[1]));
    if(file.is_open()){
    std::string row;
        for(int i = 0; (getline(file, row)); i++){
            std::stringstream ss(row);
            std::string cost;
            graphMatrix.push_back({});
            while (ss >> cost) graphMatrix[i].push_back(stod(cost));
        }
        file.close();
    }
    else{
        std::cout << "File not found.\n";
        return 0;
    }

    for(auto x : graphMatrix) if(graphMatrix.size() != x.size()) return 1;

    algorithmResult result = tabuSearch(graphMatrix);

    if (!std::filesystem::exists("cppResult")) {
        std::filesystem::create_directory("cppResult");
    }

    std::string resultName = argv[1];
    resultName.erase(resultName.length()-4, 4);
    std::ofstream f1("cppResult/result.csv", std::ios::app);
    f1 << resultName <<";" << result.time << ";" << result.cost << "\n";
    f1.close();

    std::ofstream f2("cppResult/" + resultName + ".csv", std::ios::app);
    f2 << result.time << ";" << result.cost << "\n";
    f2.close();

    std::cout << "cost: " << result.cost << ", time: " << result.time << ", path: [";
    for(int x : result.path) std::cout << x << ", ";
    std::cout << result.path[0] << "]\n";
}

// Funkcja do obliczania kosztu ścieżki
double calculateCost(const std::vector<int>& path, const std::vector<std::vector<double>>& graphMatrix) {
    double totalCost = 0.0;
    for (size_t i = 0; i < path.size() - 1; i++) {
        totalCost += graphMatrix[path[i]][path[i + 1]];
    }
    totalCost += graphMatrix[path.back()][path[0]]; 
    return totalCost;
}

// Funkcja generująca podobne ścieżki (zamiana dwóch miast)
void generateSimilarPaths(const std::vector<int>& currentPath, std::vector<std::vector<int>>& similarPaths) {
    size_t size = currentPath.size();
    similarPaths.reserve((size * (size - 1)) / 2); // Przybliżona liczba par (n*(n-1))/2

    for (size_t i = 0; i < size - 1; i++) {
        for (size_t j = i + 1; j < size; j++) {
            std::vector<int> newPath = currentPath;
            std::swap(newPath[i], newPath[j]);
            similarPaths.push_back(std::move(newPath));
        }
    }
}

// Główna funkcja tabu search
algorithmResult tabuSearch(const std::vector<std::vector<double>> graphMatrix) {
    int numCities = static_cast<int>(graphMatrix.size());
    std::vector<int> resultPath, currentPath;
    std::unordered_set<std::string> tabuSet; // Przechowuje ścieżki jako stringi dla szybkiego wyszukiwania
    double resultCost = std::numeric_limits<double>::infinity();
    int maxIterations = 50000;
    size_t maxTabuSetSize = numCities * 2;

    // Wczytanie początkowej ścieżki z pliku
    std::ifstream startPath("startPath.txt");
    if (startPath.is_open()) {
        std::string pathStr, vertex;
        getline(startPath, pathStr);
        std::stringstream ss(pathStr);
        for (int i = 0; ss >> vertex; i++) {
            currentPath.push_back(std::stoi(vertex));
        }
        startPath.close();       
    } 
    if (currentPath.size() != numCities){
        currentPath.clear();
        for(int i = 0; i < numCities; i++) currentPath.push_back(i);
    }

    resultCost = calculateCost(currentPath, graphMatrix);
    resultPath = currentPath;

    clock_t startTime = clock();
    clock_t endTime = clock();

    for (int iteration = 0; iteration < maxIterations; iteration++) {
        std::vector<std::vector<int>> similarPaths;
        generateSimilarPaths(currentPath, similarPaths);

        double bestCostSimilarPaths = std::numeric_limits<double>::infinity();
        std::vector<int> bestSimilarPath;

        for (const auto& path : similarPaths) {
            // Konwersja ścieżki do stringa w celu przechowywania w tabu
            std::string pathKey = "";
            for (int city : path) pathKey += std::to_string(city) + " ";
            if (tabuSet.find(pathKey) == tabuSet.end()) { // Sprawdzenie tabu
                double tmpCost = calculateCost(path, graphMatrix);
                if (tmpCost < bestCostSimilarPaths) {
                    bestCostSimilarPaths = tmpCost;
                    bestSimilarPath = path;
                }
            }
        }

        if (bestSimilarPath.empty()) break;

        currentPath = bestSimilarPath;
        // Dodanie ścieżki do tabu
        std::string currentPathKey = "";
        for (int city : currentPath) {
            currentPathKey += std::to_string(city) + " ";
        }
        tabuSet.insert(currentPathKey);

        // Utrzymanie rozmiaru tabu
        if (tabuSet.size() > maxTabuSetSize) {
            tabuSet.erase(tabuSet.begin());
        }

        // Aktualizacja najlepszego wyniku
        if (resultCost > bestCostSimilarPaths) {
            resultPath = currentPath;
            resultCost = bestCostSimilarPaths;
            endTime = clock();
        }
    }

    algorithmResult result;
    result.time = static_cast<int>((endTime - startTime) * 1000000 / CLOCKS_PER_SEC); // W mikrosekundach
    result.cost = resultCost;
    result.path = resultPath;

    return result;
}
