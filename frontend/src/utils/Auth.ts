export function isTokenExpired(token: string): boolean {
  try {
    const payload = JSON.parse(atob(token.split('.')[1]));
    const exp = payload.exp;
    if (!exp) return true;

    const currentTime = Math.floor(Date.now() / 1000);
    return currentTime >= exp;
  } catch (err) {
    return true;
  }
}
