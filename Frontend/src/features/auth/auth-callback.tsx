import { useEffect, useState } from "react"
import { useNavigate, useSearchParams } from "react-router-dom"
import { supabase } from "@/lib/supabase"
import { Loader2, AlertCircle } from "lucide-react"

export function AuthCallback() {
  const navigate = useNavigate()
  const [searchParams] = useSearchParams()
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    // Check for error in URL params (Supabase sends errors as query params)
    const urlError = searchParams.get("error_description") || searchParams.get("error")
    if (urlError) {
      setError(decodeURIComponent(urlError))
      return
    }

    // For PKCE flow: exchange the code for a session
    const code = searchParams.get("code")
    if (code) {
      supabase.auth.exchangeCodeForSession(code).then(({ data, error }) => {
        if (error) {
          console.error("Code exchange error:", error)
          setError(error.message)
        } else if (data.session) {
          navigate("/", { replace: true })
        }
      })
      return
    }

    // For implicit flow: check hash fragment
    const hashParams = new URLSearchParams(window.location.hash.substring(1))
    const hashError = hashParams.get("error_description") || hashParams.get("error")
    if (hashError) {
      setError(decodeURIComponent(hashError))
      return
    }

    // Fallback: listen for auth state change
    const { data: { subscription } } = supabase.auth.onAuthStateChange((event, session) => {
      if (event === "SIGNED_IN" && session) {
        navigate("/", { replace: true })
      }
    })

    // Also check existing session
    supabase.auth.getSession().then(({ data: { session } }) => {
      if (session) {
        navigate("/", { replace: true })
      }
    })

    // Safety timeout
    const timeout = setTimeout(() => {
      navigate("/login", { replace: true })
    }, 10000)

    return () => {
      subscription.unsubscribe()
      clearTimeout(timeout)
    }
  }, [navigate, searchParams])

  if (error) {
    return (
      <div style={{
        display: "flex",
        flexDirection: "column",
        alignItems: "center",
        justifyContent: "center",
        height: "100vh",
        width: "100%",
        background: "#0a0e1a",
        gap: "1rem",
        padding: "2rem",
      }}>
        <AlertCircle size={40} style={{ color: "#ef4444" }} />
        <h2 style={{ color: "#f1f5f9", fontSize: "1.25rem", margin: 0 }}>Sign In Failed</h2>
        <p style={{
          color: "#94a3b8",
          fontSize: "0.875rem",
          textAlign: "center",
          maxWidth: "400px",
          lineHeight: 1.6,
        }}>
          {error}
        </p>
        <button
          onClick={() => navigate("/login", { replace: true })}
          style={{
            marginTop: "0.5rem",
            padding: "0.6rem 1.5rem",
            borderRadius: "10px",
            border: "1px solid rgba(99, 102, 241, 0.3)",
            background: "rgba(99, 102, 241, 0.15)",
            color: "#818cf8",
            fontSize: "0.875rem",
            fontWeight: 500,
            cursor: "pointer",
          }}
        >
          Back to Login
        </button>
      </div>
    )
  }

  return (
    <div style={{
      display: "flex",
      flexDirection: "column",
      alignItems: "center",
      justifyContent: "center",
      height: "100vh",
      width: "100%",
      background: "#0a0e1a",
      gap: "1rem",
    }}>
      <Loader2 size={32} className="animate-spin" style={{ color: "#6366f1" }} />
      <p style={{ color: "#94a3b8", fontSize: "0.875rem" }}>Completing sign in...</p>
    </div>
  )
}
