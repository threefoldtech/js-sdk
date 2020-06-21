import { Service } from "../common/api";

class AuthService extends Service {

    getAuthenticatedUser() {
        return this.getCall("/auth/authenticated")
    }
}

export const auth = new AuthService();
