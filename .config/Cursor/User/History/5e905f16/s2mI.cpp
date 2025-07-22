#include <iostream>
#include <fstream>
#include <string>
#include <map>
#include <vector>
#include <sstream>
#include <regex>
#include <cmath>
#include <functional>
#include <variant>
#include <algorithm>

// Типы данных
using Value = std::variant<int, double, std::string>;

// Структура для хранения переменных
struct Variable {
    std::string name;
    std::string type;
    Value value;
};

// Структура для хранения функций
struct Function {
    std::string name;
    std::vector<std::string> body;
};

class BXLInterpreter {
private:
    std::map<std::string, Variable> variables;
    std::map<std::string, Function> functions;
    std::map<std::string, std::function<double(double)>> mathFunctions;
    std::map<std::string, std::function<double(double, double)>> mathFunctions2;
    std::map<std::string, double> mathConstants;
    
    void initializeMath() {
        // Математические функции с одним аргументом
        mathFunctions["abs"] = [](double x) { return std::abs(x); };
        mathFunctions["tan"] = [](double x) { return std::tan(x); };
        mathFunctions["cos"] = [](double x) { return std::cos(x); };
        mathFunctions["sin"] = [](double x) { return std::sin(x); };
        mathFunctions["arct"] = [](double x) { return std::atan(x); };
        mathFunctions["floor"] = [](double x) { return std::floor(x); };
        mathFunctions["ceil"] = [](double x) { return std::ceil(x); };
        mathFunctions["round"] = [](double x) { return std::round(x); };
        mathFunctions["sqrt"] = [](double x) { return std::sqrt(x); };
        mathFunctions["exp"] = [](double x) { return std::exp(x); };
        mathFunctions["log"] = [](double x) { return std::log(x); };
        mathFunctions["log10"] = [](double x) { return std::log10(x); };
        mathFunctions["log2"] = [](double x) { return std::log2(x); };
        mathFunctions["fact"] = [](double x) { 
            if (x <= 1) return 1.0;
            double result = 1;
            for (int i = 2; i <= (int)x; i++) result *= i;
            return result;
        };
        mathFunctions["gamma"] = [](double x) { return std::tgamma(x); };
        mathFunctions["erf"] = [](double x) { return std::erf(x); };
        
        // Математические функции с двумя аргументами
        mathFunctions2["arct2"] = [](double y, double x) { return std::atan2(y, x); };
        mathFunctions2["pow"] = [](double base, double exp) { return std::pow(base, exp); };
        mathFunctions2["hypot"] = [](double x, double y) { return std::hypot(x, y); };
        
        // Математические константы
        mathConstants["pi"] = M_PI;
        mathConstants["e"] = M_E;
        mathConstants["inf"] = INFINITY;
        mathConstants["phi"] = (1.0 + std::sqrt(5.0)) / 2.0;
        mathConstants["deg_to_rad"] = M_PI / 180.0;
        mathConstants["rad_to_deg"] = 180.0 / M_PI;
    }
    
    std::vector<std::string> tokenize(const std::string& line) {
        std::vector<std::string> tokens;
        std::istringstream iss(line);
        std::string token;
        
        while (iss >> token) {
            tokens.push_back(token);
        }
        
        return tokens;
    }
    
    std::string removeComments(const std::string& line) {
        std::string result = line;
        size_t pos = result.find(">>");
        if (pos != std::string::npos) {
            result = result.substr(0, pos);
        }
        return result;
    }
    
    std::vector<std::string> preprocessFile(const std::string& filename) {
        std::ifstream file(filename);
        if (!file.is_open()) {
            throw std::runtime_error("Cannot open file: " + filename);
        }
        
        std::vector<std::string> lines;
        std::string line;
        bool inMultilineComment = false;
        
        while (std::getline(file, line)) {
            // Убираем пробелы в начале и конце
            line = std::regex_replace(line, std::regex("^\\s+|\\s+$"), "");
            
            if (line.empty()) continue;
            
            // Обработка многострочных комментариев
            if (line.find(">>") == 0 && line.find("<<") == std::string::npos) {
                inMultilineComment = true;
                continue;
            }
            
            if (line.find("<<") != std::string::npos) {
                inMultilineComment = false;
                continue;
            }
            
            if (inMultilineComment) continue;
            
            // Удаляем однострочные комментарии
            line = removeComments(line);
            line = std::regex_replace(line, std::regex("^\\s+|\\s+$"), "");
            
            if (!line.empty()) {
                lines.push_back(line);
            }
        }
        
        return lines;
    }
    
    Value evaluateExpression(const std::string& expr) {
        std::string cleanExpr = expr;
        
        // Замена переменных
        std::regex varRegex("\\$([a-zA-Z_][a-zA-Z0-9_]*)");
        std::smatch match;
        
        while (std::regex_search(cleanExpr, match, varRegex)) {
            std::string varName = match[1].str();
            if (variables.find(varName) != variables.end()) {
                std::string replacement;
                if (variables[varName].type == "int") {
                    replacement = std::to_string(std::get<int>(variables[varName].value));
                } else if (variables[varName].type == "float") {
                    replacement = std::to_string(std::get<double>(variables[varName].value));
                } else if (variables[varName].type == "str") {
                    replacement = std::get<std::string>(variables[varName].value);
                }
                cleanExpr = std::regex_replace(cleanExpr, std::regex("\\$" + varName), replacement);
            }
        }
        
        // Обработка математических констант
        for (const auto& [name, value] : mathConstants) {
            cleanExpr = std::regex_replace(cleanExpr, std::regex("math\\." + name), std::to_string(value));
        }
        
        // Новое: обработка операторов сравнения
        Value cmpResult;
        if (evaluateComparisonExpression(cleanExpr, cmpResult)) {
            return cmpResult;
        }
        
        // Простая обработка математических операций
        try {
            return evaluateSimpleExpression(cleanExpr);
        } catch (...) {
            return std::string(cleanExpr);
        }
    }
    
    // Новая функция для сравнения
    bool evaluateComparisonExpression(const std::string& expr, Value& result) {
        static const std::vector<std::pair<std::string, std::function<bool(double, double)>>> cmpOps = {
            {"==", [](double a, double b) { return a == b; }},
            {"!=", [](double a, double b) { return a != b; }},
            {">=", [](double a, double b) { return a >= b; }},
            {"<=", [](double a, double b) { return a <= b; }}
        };
        for (const auto& [op, func] : cmpOps) {
            size_t pos = expr.find(op);
            if (pos != std::string::npos) {
                double left = 0, right = 0;
                try {
                    left = evaluateSimpleExpression(expr.substr(0, pos));
                    right = evaluateSimpleExpression(expr.substr(pos + op.size()));
                } catch (...) {
                    return false;
                }
                result = func(left, right) ? 1 : 0;
                return true;
            }
        }
        return false;
    }
    
    double evaluateSimpleExpression(const std::string& expr) {
        // Простой калькулятор выражений
        std::string cleanExpr = expr;
        
        // Удаляем пробелы
        cleanExpr.erase(std::remove(cleanExpr.begin(), cleanExpr.end(), ' '), cleanExpr.end());
        
        // Обработка математических функций
        std::regex mathFuncRegex("math\\.([a-zA-Z0-9_]+)\\(([^)]+)\\)");
        std::smatch match;
        
        while (std::regex_search(cleanExpr, match, mathFuncRegex)) {
            std::string funcName = match[1].str();
            std::string args = match[2].str();
            
            if (mathFunctions.find(funcName) != mathFunctions.end()) {
                double arg = evaluateSimpleExpression(args);
                double result = mathFunctions[funcName](arg);
                cleanExpr = std::regex_replace(cleanExpr, std::regex("math\\." + funcName + "\\([^)]+\\)"), std::to_string(result));
            } else if (mathFunctions2.find(funcName) != mathFunctions2.end()) {
                // Для функций с двумя аргументами
                size_t commaPos = args.find(',');
                if (commaPos != std::string::npos) {
                    double arg1 = evaluateSimpleExpression(args.substr(0, commaPos));
                    double arg2 = evaluateSimpleExpression(args.substr(commaPos + 1));
                    double result = mathFunctions2[funcName](arg1, arg2);
                    cleanExpr = std::regex_replace(cleanExpr, std::regex("math\\." + funcName + "\\([^)]+\\)"), std::to_string(result));
                }
            }
        }
        
        // Новое: обработка целочисленного деления //
        size_t intDivPos = cleanExpr.find("//");
        if (intDivPos != std::string::npos) {
            double left = evaluateSimpleExpression(cleanExpr.substr(0, intDivPos));
            double right = evaluateSimpleExpression(cleanExpr.substr(intDivPos + 2));
            if (right == 0) throw std::runtime_error("Division by zero");
            return static_cast<int>(left) / static_cast<int>(right);
        }
        
        // Обработка степени
        size_t powerPos = cleanExpr.find('^');
        if (powerPos != std::string::npos) {
            double base = std::stod(cleanExpr.substr(0, powerPos));
            double exp = std::stod(cleanExpr.substr(powerPos + 1));
            return std::pow(base, exp);
        }
        
        // Обработка основных операций
        std::vector<char> operators = {'*', '/', '%', '+', '-'};
        
        for (char op : operators) {
            size_t pos = cleanExpr.find(op);
            if (pos != std::string::npos && pos > 0) {
                double left = std::stod(cleanExpr.substr(0, pos));
                double right = std::stod(cleanExpr.substr(pos + 1));
                
                switch (op) {
                    case '*': return left * right;
                    case '/': return left / right;
                    case '%': return std::fmod(left, right);
                    case '+': return left + right;
                    case '-': return left - right;
                }
            }
        }
        
        return std::stod(cleanExpr);
    }
    
    void executeStatement(const std::string& statement) {
        std::vector<std::string> tokens = tokenize(statement);
        
        if (tokens.empty()) return;
        
        // Объявление переменных
        if (tokens[0].find('.') != std::string::npos && tokens.size() >= 3 && tokens[1] == "=") {
            size_t dotPos = tokens[0].find('.');
            std::string varName = tokens[0].substr(0, dotPos);
            std::string varType = tokens[0].substr(dotPos + 1);
            
            std::string valueStr = tokens[2];
            for (size_t i = 3; i < tokens.size(); i++) {
                valueStr += " " + tokens[i];
            }
            
            Variable var;
            var.name = varName;
            var.type = varType;
            
            if (varType == "int") {
                var.value = std::stoi(valueStr);
            } else if (varType == "float") {
                var.value = std::stod(valueStr);
            } else if (varType == "str") {
                // Убираем кавычки
                if (valueStr.front() == '\'' && valueStr.back() == '\'') {
                    valueStr = valueStr.substr(1, valueStr.length() - 2);
                }
                var.value = valueStr;
            }
            
            variables[varName] = var;
        }
        // Вызов функции out.str
        else if (tokens[0] == "out.str") {
            std::string output = statement.substr(statement.find('(') + 1);
            output = output.substr(0, output.find_last_of(')'));
            
            // Убираем внешние кавычки
            if (output.front() == '"' && output.back() == '"') {
                output = output.substr(1, output.length() - 2);
            }
            
            // Обработка переменных в строке
            std::regex varRegex("\\$([a-zA-Z_][a-zA-Z0-9_]*)");
            std::smatch match;
            
            while (std::regex_search(output, match, varRegex)) {
                std::string varName = match[1].str();
                if (variables.find(varName) != variables.end()) {
                    std::string replacement;
                    if (variables[varName].type == "int") {
                        replacement = std::to_string(std::get<int>(variables[varName].value));
                    } else if (variables[varName].type == "float") {
                        replacement = std::to_string(std::get<double>(variables[varName].value));
                    } else if (variables[varName].type == "str") {
                        replacement = std::get<std::string>(variables[varName].value);
                    }
                    output = std::regex_replace(output, std::regex("\\$" + varName), replacement);
                }
            }
            
            // Обработка функций в фигурных скобках
            std::regex funcRegex("\\{([^}]+)\\}");
            while (std::regex_search(output, match, funcRegex)) {
                std::string funcExpr = match[1].str();
                Value result = evaluateExpression(funcExpr);
                
                std::string replacement;
                if (std::holds_alternative<int>(result)) {
                    replacement = std::to_string(std::get<int>(result));
                } else if (std::holds_alternative<double>(result)) {
                    replacement = std::to_string(std::get<double>(result));
                } else {
                    replacement = std::get<std::string>(result);
                }
                
                output = std::regex_replace(output, std::regex("\\{[^}]+\\}"), replacement);
            }
            
            std::cout << output << std::endl;
        }
        // Вызов функции
        else if (functions.find(tokens[0]) != functions.end()) {
            executeFunction(tokens[0]);
        }
        // Обычное присваивание
        else if (tokens.size() >= 3 && tokens[1] == "=") {
            std::string varName = tokens[0];
            std::string expr = tokens[2];
            for (size_t i = 3; i < tokens.size(); i++) {
                expr += " " + tokens[i];
            }
            
            Value result = evaluateExpression(expr);
            
            // Определяем тип результата
            Variable var;
            var.name = varName;
            
            if (std::holds_alternative<int>(result)) {
                var.type = "int";
                var.value = std::get<int>(result);
            } else if (std::holds_alternative<double>(result)) {
                var.type = "float";
                var.value = std::get<double>(result);
            } else {
                var.type = "str";
                var.value = std::get<std::string>(result);
            }
            
            variables[varName] = var;
        }
    }
    
    void executeFunction(const std::string& funcName) {
        if (functions.find(funcName) != functions.end()) {
            for (const std::string& line : functions[funcName].body) {
                executeStatement(line);
            }
        }
    }
    
public:
    BXLInterpreter() {
        initializeMath();
    }
    
    void run(const std::string& filename) {
        try {
            std::vector<std::string> lines = preprocessFile(filename);
            
            // Парсим функции
            for (size_t i = 0; i < lines.size(); i++) {
                const std::string& line = lines[i];
                
                if (line.find("func ") == 0 || line.find("main(") == 0) {
                    size_t nameStart = line.find("func ") == 0 ? 5 : 0;
                    size_t nameEnd = line.find('(');
                    if (nameEnd == std::string::npos) continue;
                    
                    std::string funcName = line.substr(nameStart, nameEnd - nameStart);
                    
                    Function func;
                    func.name = funcName;
                    
                    i++; // Пропускаем строку с '{'
                    
                    // Читаем тело функции до '}'
                    while (i < lines.size() && lines[i] != "}") {
                        if (!lines[i].empty()) {
                            func.body.push_back(lines[i]);
                        }
                        i++;
                    }
                    
                    functions[funcName] = func;
                }
            }
            
            // Ищем и выполняем main()
            if (functions.find("main") != functions.end()) {
                executeFunction("main");
            } else {
                std::cerr << "Error: main() function not found" << std::endl;
            }
            
        } catch (const std::exception& e) {
            std::cerr << "Error: " << e.what() << std::endl;
        }
    }
};

int main(int argc, char* argv[]) {
    if (argc != 2) {
        std::cerr << "Usage: bxl <path_to_script.bxl>" << std::endl;
        return 1;
    }
    
    BXLInterpreter interpreter;
    interpreter.run(argv[1]);
    
    return 0;
}
