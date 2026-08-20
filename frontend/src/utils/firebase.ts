import { initializeApp } from 'firebase/app';
import { 
  getAuth, 
  signInWithEmailAndPassword, 
  createUserWithEmailAndPassword, 
  signOut,
  onAuthStateChanged as fbOnAuthStateChanged,
  User as FirebaseUser
} from 'firebase/auth';

export interface User {
  uid: string;
  email: string;
  displayName?: string;
}

const firebaseConfig = {
  apiKey: import.meta.env.VITE_FIREBASE_API_KEY,
  authDomain: import.meta.env.VITE_FIREBASE_AUTH_DOMAIN,
  projectId: import.meta.env.VITE_FIREBASE_PROJECT_ID,
  storageBucket: import.meta.env.VITE_FIREBASE_STORAGE_BUCKET,
  messagingSenderId: import.meta.env.VITE_FIREBASE_MESSAGING_SENDER_ID,
  appId: import.meta.env.VITE_FIREBASE_APP_ID
};

const isFirebaseConfigured = !!firebaseConfig.apiKey;

let auth: any = null;

if (isFirebaseConfigured) {
  try {
    const app = initializeApp(firebaseConfig);
    auth = getAuth(app);
    console.log("[FIREBASE] Client SDK successfully initialized.");
  } catch (error) {
    console.warn("[FIREBASE WARNING] Initialization failed, using local mock auth:", error);
  }
} else {
  console.log("[FIREBASE WARNING] Missing VITE_FIREBASE_API_KEY. Using LOCAL MOCK authentication mode.");
}

// Local mock states
type AuthStateListener = (user: User | null) => void;
const listeners = new Set<AuthStateListener>();
let currentMockUser: User | null = null;

const cachedUser = localStorage.getItem("nyaya_auth_user");
if (cachedUser) {
  try {
    currentMockUser = JSON.parse(cachedUser);
  } catch {
    currentMockUser = null;
  }
}

export function onAuthStateChanged(callback: AuthStateListener) {
  if (auth) {
    return fbOnAuthStateChanged(auth, (fbUser: FirebaseUser | null) => {
      if (fbUser) {
        callback({
          uid: fbUser.uid,
          email: fbUser.email || '',
          displayName: fbUser.displayName || undefined
        });
      } else {
        callback(null);
      }
    });
  } else {
    listeners.add(callback);
    callback(currentMockUser);
    return () => {
      listeners.delete(callback);
    };
  }
}

export async function signUpWithEmail(email: string, password: string): Promise<User> {
  if (auth) {
    const userCredential = await createUserWithEmailAndPassword(auth, email, password);
    const fbUser = userCredential.user;
    return {
      uid: fbUser.uid,
      email: fbUser.email || '',
      displayName: fbUser.displayName || undefined
    };
  } else {
    currentMockUser = {
      uid: "user-uid",
      email,
      displayName: email.split("@")[0]
    };
    localStorage.setItem("nyaya_auth_user", JSON.stringify(currentMockUser));
    localStorage.setItem("nyaya_auth_token", "mock-user-token");
    listeners.forEach(cb => cb(currentMockUser));
    return currentMockUser;
  }
}

export async function loginWithEmail(email: string, password: string): Promise<User> {
  if (auth) {
    const userCredential = await signInWithEmailAndPassword(auth, email, password);
    const fbUser = userCredential.user;
    return {
      uid: fbUser.uid,
      email: fbUser.email || '',
      displayName: fbUser.displayName || undefined
    };
  } else {
    currentMockUser = {
      uid: "user-uid",
      email,
      displayName: email.split("@")[0]
    };
    localStorage.setItem("nyaya_auth_user", JSON.stringify(currentMockUser));
    localStorage.setItem("nyaya_auth_token", "mock-user-token");
    listeners.forEach(cb => cb(currentMockUser));
    return currentMockUser;
  }
}

export async function logout(): Promise<void> {
  if (auth) {
    await signOut(auth);
  } else {
    currentMockUser = null;
    localStorage.removeItem("nyaya_auth_user");
    localStorage.removeItem("nyaya_auth_token");
    listeners.forEach(cb => cb(null));
  }
}

export async function getIdToken(): Promise<string | null> {
  if (auth && auth.currentUser) {
    return await auth.currentUser.getIdToken();
  } else {
    return localStorage.getItem("nyaya_auth_token") || "mock-user-token";
  }
}
