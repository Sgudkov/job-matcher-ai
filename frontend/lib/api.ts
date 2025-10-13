import { Search } from "../app/types/types";

const API_URL = "http://localhost:8000/api/v1";


interface Token{
  sub: number,
  access_token: string,
  token_type: string,
  expires_in: number
}


export async function register(email: string, password: string) {
  const res = await fetch(`${API_URL}/auth/register`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ email, password }),
  });
  return res.json();
}



export async function login(username: string, password: string) {
  const formData = new URLSearchParams();
  formData.append('username', username);
  formData.append('password', password);

  const res = await fetch(`${API_URL}/auth/token`, {
    method: "POST",
    // headers: { "Content-Type": "application/json" },
    body: formData,
  });
  const data = await res.json();
  if (data.access_token) {
    localStorage.setItem("token", data.access_token);
  }
  return data;
}

export async function fetchUser(token: string) {
  const tokenData = decodeToken(token);
  const res = await fetch(`${API_URL}/candidates/${tokenData.sub}`, {
    method: "GET",
    headers: {
      "Content-Type": "application/json",
      Authorization: `Bearer ${token}`,
    },
  });
  const data = await res.json();
  return data;

}

function decodeToken(token: string): Token | null {
  try {
    const decodedToken = JSON.parse(atob(token.split('.')[1]));
    return decodedToken;
  } catch (error) {
    return null;
  }
}

export async function me() {
  const token = localStorage.getItem("token");
  if (!token) return null;

  const res = await fetch(`${API_URL}/auth/me`, {
    headers: { Authorization: `Bearer ${token}` },
  });
  return res.json();
}

export async function getSearchData(searchParams:Search) {
  const res = await fetch(`${API_URL}/resumes/search`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(searchParams),
  });
  const data = await res.json();
  return data;
}

export async function getSearchResume(searchParams:Search) {
  const res = await fetch(`${API_URL}/resumes/search`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(searchParams),
  });
  const data = await res.json();
  return data;
}

export function logout() {
  localStorage.removeItem("token");
}
