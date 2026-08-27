const TOKEN_STORAGE_KEY =
  "openprotecteur_access_token";


export function getAccessToken(): string | null {
  return sessionStorage.getItem(
    TOKEN_STORAGE_KEY,
  );
}


export function saveAccessToken(
  token: string,
): void {
  sessionStorage.setItem(
    TOKEN_STORAGE_KEY,
    token,
  );
}


export function removeAccessToken(): void {
  sessionStorage.removeItem(
    TOKEN_STORAGE_KEY,
  );
}
