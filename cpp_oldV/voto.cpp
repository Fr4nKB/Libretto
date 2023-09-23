#include <iostream>
#include <vector>
#include <stdio.h>
#include <iomanip>
#include <string>
#include <fstream>
#include <bits/stdc++.h>
#include <ncurses.h>
#include <unistd.h>
using namespace std;

#define TOTCFU 120

const int MAX_CHAR = 30;

struct materia {
    string name;
    int grade, cfu;
    materia *next;
};

class libretto {
    materia *list;
    materia lowest;
    void calc(float& ris, float& ris2, float& ris3, float& ris4);
    void clearLowest();

public:
    libretto();
    libretto(const string, int, int);
    void print();
    bool insert(const string, int, int);
    bool remove(string);
    void average();
    void readFromFile();
    void save();
    ~libretto();
};

libretto mio;

void libretto::calc(float& m, float& bl, float &min, float &max) {
    materia *q = this->list;
    int tmp;
    double totc = 0, totcPrev = 0;
    m = 0;
    while(q) {
        if(q->grade >= 18) {  
            tmp = (q->grade <= 30) ? q->grade*q->cfu : 30*q->cfu;
            m += tmp;
            totc += q->cfu;
        }
        q = q->next;
    }

    min = (m + 18*(TOTCFU - totc))/TOTCFU;
    max = (m + 30*(TOTCFU - totc))/TOTCFU;
    m = m / totc;
    bl = m*3+18;
}

void libretto::clearLowest() {
    materia *q = this->list;
    this->lowest.grade = 33;
    this->lowest.cfu = 12;
    while(q) {
        if(q->grade < this->lowest.grade || (q->grade == this->lowest.grade && q->cfu > this->lowest.cfu)) this->lowest = *q;
        q = q->next;
    }
}

libretto::libretto() {
    this->list = nullptr;

    //set to the maximum possibile
    this->lowest.grade = 33;
    this->lowest.grade = 12;
}

libretto::libretto(const string name, int grade, int cfu) {
    this->list = nullptr;
    insert(name, grade, cfu);
}

void libretto::print() {
    materia *q = this->list;
    cout<<"-----"<<endl;
    cout<<"Nome"<<setw(MAX_CHAR+2)<<"Voto\t"<<"CFU"<<endl;
    while(q) {
        int n = MAX_CHAR - q->name.length()+4;
        if(q->grade >= 18) cout<<q->name<<setw(n)<<q->grade<<"\t"<<q->cfu<<endl;
        q = q->next;
    }

    float m, bl, min, max;
    calc(m, bl, min, max);
    cout<<"-----"<<endl;
    cout<<"Media Ponderata: "<<m<<endl;
    cout<<"Media con solo 18 d'ora in poi: "<<min<<endl;
    cout<<"Media con solo 30 d'ora in poi: "<<max<<endl;
    cout<<"Base di Laurea: "<<bl<<endl;
    cout<<"Voto massimo: ";
    if(round(bl+10) >= 111) {
        if(m >= 28) cout<<"110L"<<endl;
        else cout<<"110"<<endl;
    }
    else cout<<round(bl+10)<<endl;
}

bool libretto::insert(const string name, int grade, int cfu) {
    if(cfu <= 0) return false;
    if((grade < 18 && grade != -1) || (grade > 30 && grade != 33)) return false;
    if(name.empty() || name == ""  || name == " ") return false;

    materia *nuovo = new materia;
    int len = name.length();
    len = (len >= MAX_CHAR) ? MAX_CHAR : len;
    nuovo->name = name;
    nuovo->name.resize(len);
    nuovo->grade = grade;
    nuovo->cfu = cfu;
    nuovo->next = nullptr;

    if(!this->list) {   //first grade
        this->list = nuovo;
        this->lowest = *nuovo;
        return true;
    }

    materia *q = this->list;
    while(q->next) {
        if(!name.compare(q->name)) {
            return false;
        }
        q = q->next;
    }
    q->next = nuovo;
    //update lowest grade
    if(nuovo->grade != -1 && nuovo->grade < this->lowest.grade || (nuovo->grade == this->lowest.grade && nuovo->cfu > this->lowest.cfu)) this->lowest = *nuovo;
    return true;
}

bool libretto::remove(string name) {
    materia *q = this->list, *p;
    if(name.length() >= MAX_CHAR) name.resize(MAX_CHAR);
    if(!name.compare(q->name)) {
        this->list = this->list->next;
        q->name.clear();
        delete q;
        if(!name.compare(this->lowest.name)) clearLowest();
        return true;
    }   

    while(q) {
        p = q;
        q = q->next;
        if(q && !name.compare(q->name)) {
            p->next = q->next;
            q->name.clear();
            delete q;
            if(!name.compare(this->lowest.name)) clearLowest();
            return true;
        }
    }
    
    return false;
}

void libretto::average() {
    float m, bl, min, max;
    calc(m, bl, min, max);
    cout<<"La media ponderata e' "<<setprecision(4)<<m<<" e la base di laurea e' "<<bl<<"."<<endl;
    cout<<"Media con solo 18 d'ora in poi: "<<min<<endl;
    cout<<"Media con solo 30 d'ora in poi: "<<max<<endl;
}

libretto::~libretto() {
    materia *q;
    save();
    while(this->list) {
        q = this->list;
        this->list = this->list->next;
        q->name.clear();
        delete q;
    }
}

void libretto::readFromFile() {
    ifstream file("esami.txt");
    if(file.is_open()) {
        char *token;
        string line, name;
        int i, v, c;
        while(getline(file, line)) {
            token = &line[0];
            i = 0;
            token = strtok(token, ",");
            while(token) {
                if(i == 0) name = token;
                else if(i == 1) v = atoi(token);
                else c = atoi(token);
                i++;
                token = strtok(NULL, ",");
            }
            if(i != 0) insert(name, v, c);
        }
        file.close();
    }
}

void libretto::save() {
    ofstream file("esami.txt", ios::out);
    if(file.is_open()) {
        materia *q = this->list;
        while(q) {
            file<<q->name<<", "<<q->grade<<", "<<q->cfu<<endl;
            q = q->next;
        }
        file.close();
    }
}

vector<string> commands = {"Libretto", "Aggiungi un voto", "Rimuovi un voto", "Stampa media"};

void printMenu(uint index) {
    std::cout << "Use arrows to move across the options, press enter to confirm and q to quit\r\n";
    for (uint i = 0; i < commands.size(); i++) {
        std::cout << ((i == index) ? "●" : "○") << " " << commands[i] << "\r\n";
    }
}

void runCommand(uint index) {
    char c;
    bool valid;
    string name, grade, cfu;
    int cf, vt;
    char insname [] = "Qual e' il nome della materia?";
    char insgrade [] = "Qual e' il voto?";
    char exitIns [] = "Premi x per tornare indietro";
    char invalidInput [] = "Inserimento non valido, riprovare...";
    string ex("x");

    system("clear");
    switch(index) {
        case 0:
            mio.print();
            break;
        case 1:
            cout<<exitIns<<endl;
            cout<<insname<<endl;
            getline(cin, name);
            if(!name.compare(ex)) return;
            fflush(stdin);
            
            valid = false;
            cout<<insgrade<<endl;
            while(!valid) {
                valid = true;
                getline(cin, grade);
                fflush(stdin);
                if(!grade.compare(ex)) return;
                try {vt = stoi(grade);}
                catch(exception &err) { 
                    cout<<invalidInput<<endl;
                    valid = false;
                }
            }
            
            valid = false;
            cout<<"Quanti sono i CFU?"<<endl;
            while(!valid) {
                valid = true;
                getline(cin, cfu);
                fflush(stdin);
                if(!cfu.compare(ex)) return;
                try {cf = stoi(cfu);}
                catch(exception &err) { 
                    cout<<invalidInput<<endl;
                    valid = false;
                }
            }

            if(mio.insert(name, vt, cf)) {
                cout<<"Voto inserito correttamente!"<<endl;
            }
            else cout<<"Inserimento fallito!"<<endl;

            break;
        case 2:
            cout<<exitIns<<endl;
            cout<<insname<<endl;
            fflush(stdin);
            getline(cin, name);
            if(!name.compare(ex)) return;
            fflush(stdin);
            if(mio.remove(name)) cout<<endl<<"Voto rimosso correttamente!"<<endl;
            else cout<<endl<<"Rimozione fallita!"<<endl;
            break;
        case 3:
            mio.average();
            break;
        default:
            cout<<"Input non valido, riprova..."<<endl;
            break;
        }
}

int main() {
    mio.readFromFile();

    uint index = 0;
    
    initscr();
    keypad(stdscr, TRUE);
    noecho();

    while (true) {
        refresh();
        system("clear");
        int commandsCount = commands.size();
        if (index < 0 || index >= commandsCount) {
            index = 0;
        }
        printMenu(index);
        int input = getch();
        switch (input) {
            case 10: // ENTER
                endwin();

                runCommand(index);

                initscr();
                keypad(stdscr, TRUE);
                noecho();
                getch();
                system("clear");
                break;
            case KEY_UP:
                system("clear");
                index = (index - 1 < 0) ? index : index - 1;
                break;
            case KEY_DOWN:
                system("clear");
                index = (index + 1 >= commandsCount) ? index : index + 1;
                break;
            case 113: // QUIT
                endwin();
                exit(0);
            default:
                system("clear");
                break;
        }
    }

    return 0;
}