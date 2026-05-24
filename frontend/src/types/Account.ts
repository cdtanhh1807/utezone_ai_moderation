
  export interface UserInfo {
    fullName: string;
    phone?: string;
    address?: string;
    email?: string;
    day_of_birth?: string;
    followers?: string[];
    followed?: string[];
    limits?: string[];
    blocks?: string[];
    description?: string;
    avatar?: string;
    department?: string;
  }

  export interface Account {
    id?: string;
    type?: string;
    email: string;
    password?: string;
    role?: string;
    status?: string;
    userInfo: UserInfo;
  }

