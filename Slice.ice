module IceGauntlet{

    interface Authenticaction {
        void changePassword(string user, string currentPassHash, string newPassHash);
        string getNewToken(string user, string passwordHash);
        bool isValid(string token);        
    };
    
    interface Room {
        void publish(string token, string roomData);
        void remove(string token, string roomName);
        string getRoom();
    };
};
