import { Service } from "../common/api";

const BASE_URL = "/auth";

class AuthService extends Service {
    constructor() {
        super(BASE_URL);
    }

    getCurrentUser() {
        return this.getCall("authorized");
    }

    logout() {
        const nextUrl = window.location.pathname + window.location.hash;
        window.location.href = `/auth/logout?next_url=${nextUrl}`;
    }
}

export const auth = new AuthService();
