// Course baseline originally created by yangyuhan, 2024-10-02.
// Portfolio revision: dynamic dimensions, validated input, empty-cluster handling,
// deterministic initialization and JSON output. Attribution is retained.
#include <algorithm>
#include <chrono>
#include <cmath>
#include <fstream>
#include <iomanip>
#include <iostream>
#include <limits>
#include <sstream>
#include <stdexcept>
#include <vector>
using Point = std::vector<double>;
double squared_distance(const Point& a, const Point& b) {
    double s = 0; for (size_t j = 0; j < a.size(); ++j) { double d=a[j]-b[j]; s+=d*d; } return s;
}
int main(int argc, char** argv) {
    try {
        if (argc < 2 || argc > 3) throw std::runtime_error("Usage: kmeans_cpu <id-plus-features.txt> [k]");
        int k = argc == 3 ? std::stoi(argv[2]) : 3;
        std::ifstream input(argv[1]);
        if (!input) throw std::runtime_error("Cannot open input");
        std::vector<Point> points; std::string line;
        while (std::getline(input, line)) {
            if (line.find_first_not_of(" \t\r") == std::string::npos) continue;
            std::istringstream stream(line); double id, v;
            if (!(stream >> id) || !std::isfinite(id)) throw std::runtime_error("Invalid row ID");
            Point p; while (stream >> v) { if (!std::isfinite(v)) throw std::runtime_error("Nonfinite feature"); p.push_back(v); }
            if (!stream.eof()) throw std::runtime_error("Nonnumeric feature");
            if (p.empty() || (!points.empty() && p.size()!=points[0].size())) throw std::runtime_error("Inconsistent feature dimensions");
            points.push_back(p);
        }
        if (k < 1 || size_t(k) > points.size()) throw std::runtime_error("k must be between 1 and number of rows");
        std::vector<Point> centers(points.begin(), points.begin()+k);
        std::vector<int> membership(points.size(),-1); int iterations = 0;
        auto start = std::chrono::steady_clock::now();
        for (; iterations < 1000; ) {
            std::vector<Point> sums(k,Point(points[0].size(),0)); std::vector<int> counts(k,0);
            bool changed = false;
            for (size_t i=0;i<points.size();++i) {
                int closest=0; double best=std::numeric_limits<double>::infinity();
                for (int c=0;c<k;++c) { double d=squared_distance(points[i],centers[c]); if (d<best) {best=d; closest=c;} }
                changed |= membership[i]!=closest; membership[i]=closest; ++counts[closest];
                for (size_t d=0;d<points[i].size();++d) sums[closest][d]+=points[i][d];
            }
            // Empty clusters keep their previous center instead of dividing by zero.
            for (int c=0;c<k;++c) if(counts[c]) for(size_t d=0;d<centers[c].size();++d) centers[c][d]=sums[c][d]/counts[c];
            ++iterations; if (!changed) break;
        }
        double inertia=0;
        for (size_t i=0;i<points.size();++i) {
            int closest=0; double best=std::numeric_limits<double>::infinity();
            for(int c=0;c<k;++c) {double d=squared_distance(points[i],centers[c]);if(d<best){best=d;closest=c;}}
            membership[i]=closest; inertia+=best;
        }
        double ms=std::chrono::duration<double,std::milli>(std::chrono::steady_clock::now()-start).count();
        std::cout<<std::setprecision(12)<<"{\"rows\":"<<points.size()<<",\"dimensions\":"<<points[0].size()<<",\"k\":"<<k<<",\"iterations\":"<<iterations<<",\"inertia\":"<<inertia<<",\"elapsed_ms\":"<<ms<<",\"centers\":[";
        for(int c=0;c<k;++c){if(c)std::cout<<',';std::cout<<'[';for(size_t d=0;d<centers[c].size();++d){if(d)std::cout<<',';std::cout<<centers[c][d];}std::cout<<']';}
        std::cout<<"],\"membership\":[";for(size_t i=0;i<membership.size();++i){if(i)std::cout<<',';std::cout<<membership[i];}std::cout<<"]}\n";
    } catch(const std::exception& e) {std::cerr<<e.what()<<'\n';return 1;}
}
