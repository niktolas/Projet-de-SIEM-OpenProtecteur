import { useState } from "react";
import type { FormEvent } from "react";

import { login } from "./api";
import { saveAccessToken } from "./auth";


interface LoginPageProps {
  onLogin: () => Promise<void>;
}


function LoginPage({
  onLogin,
}: LoginPageProps) {
  const [username, setUsername] =
    useState("");

  const [password, setPassword] =
    useState("");

  const [loading, setLoading] =
    useState(false);

  const [error, setError] =
    useState<string | null>(null);


  async function handleSubmit(
    event: FormEvent<HTMLFormElement>,
  ) {
    event.preventDefault();

    setLoading(true);
    setError(null);

    try {
      const token = await login(
        username,
        password,
      );

      saveAccessToken(
        token.access_token,
      );

      await onLogin();
    } catch (requestError) {
      setError(
        requestError instanceof Error
          ? requestError.message
          : "Connexion impossible.",
      );
    } finally {
      setLoading(false);
    }
  }


  return (
    <main className="login-page">
      <section className="login-card">
        <div className="login-brand">
          <div className="brand-icon">
            OP
          </div>

          <div>
            <h1>OpenProtecteur</h1>
            <p>
              Security Operations Platform
            </p>
          </div>
        </div>

        <div className="login-heading">
          <p className="eyebrow">
            Authentification
          </p>

          <h2>Connexion au centre SOC</h2>

          <p>
            Utilisez votre compte OpenProtecteur
            pour accéder aux événements et aux
            alertes.
          </p>
        </div>

        {error && (
          <div className="error-message">
            {error}
          </div>
        )}

        <form
          className="login-form"
          onSubmit={handleSubmit}
        >
          <label>
            Nom d’utilisateur

            <input
              type="text"
              autoComplete="username"
              value={username}
              required
              onChange={(event) =>
                setUsername(
                  event.target.value,
                )
              }
            />
          </label>

          <label>
            Mot de passe

            <input
              type="password"
              autoComplete="current-password"
              value={password}
              required
              onChange={(event) =>
                setPassword(
                  event.target.value,
                )
              }
            />
          </label>

          <button
            type="submit"
            className="login-button"
            disabled={loading}
          >
            {loading
              ? "Connexion..."
              : "Se connecter"}
          </button>
        </form>
      </section>
    </main>
  );
}


export default LoginPage;
