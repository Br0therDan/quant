"use client";

import { createContext, useContext, useState, useCallback, type ReactNode } from "react";
import { Snackbar, Alert, type AlertColor } from "@mui/material";

interface SnackbarMessage {
  id: string;
  message: string;
  severity: AlertColor;
  autoHideDuration?: number;
}

interface SnackbarContextType {
  showSnackbar: (message: string, severity?: AlertColor, autoHideDuration?: number) => void;
  showSuccess: (message: string, autoHideDuration?: number) => void;
  showError: (message: string, autoHideDuration?: number) => void;
  showWarning: (message: string, autoHideDuration?: number) => void;
  showInfo: (message: string, autoHideDuration?: number) => void;
}

const SnackbarContext = createContext<SnackbarContextType | undefined>(undefined);

export function useSnackbar() {
  const context = useContext(SnackbarContext);
  if (!context) {
    throw new Error("useSnackbar must be used within a SnackbarProvider");
  }
  return context;
}

interface SnackbarProviderProps {
  children: ReactNode;
}

export function SnackbarProvider({ children }: SnackbarProviderProps) {
  const [snackbars, setSnackbars] = useState<SnackbarMessage[]>([]);

  const showSnackbar = useCallback(
    (message: string, severity: AlertColor = "info", autoHideDuration = 6000) => {
      const id = Date.now().toString();
      const newSnackbar: SnackbarMessage = {
        id,
        message,
        severity,
        autoHideDuration,
      };

      setSnackbars((prev) => [...prev, newSnackbar]);

      // 자동으로 제거
      setTimeout(() => {
        setSnackbars((prev) => prev.filter((snackbar) => snackbar.id !== id));
      }, autoHideDuration);
    },
    []
  );

  const showSuccess = useCallback(
    (message: string, autoHideDuration?: number) => {
      showSnackbar(message, "success", autoHideDuration);
    },
    [showSnackbar]
  );

  const showError = useCallback(
    (message: string, autoHideDuration?: number) => {
      showSnackbar(message, "error", autoHideDuration);
    },
    [showSnackbar]
  );

  const showWarning = useCallback(
    (message: string, autoHideDuration?: number) => {
      showSnackbar(message, "warning", autoHideDuration);
    },
    [showSnackbar]
  );

  const showInfo = useCallback(
    (message: string, autoHideDuration?: number) => {
      showSnackbar(message, "info", autoHideDuration);
    },
    [showSnackbar]
  );

  const handleClose = useCallback((id: string) => {
    setSnackbars((prev) => prev.filter((snackbar) => snackbar.id !== id));
  }, []);

  const contextValue: SnackbarContextType = {
    showSnackbar,
    showSuccess,
    showError,
    showWarning,
    showInfo,
  };

  // Workaround for mismatched React type versions in the monorepo: cast Provider to any
  const Provider: any = SnackbarContext.Provider;

  return (
    <Provider value={contextValue}>
      {children}
      {snackbars.map((snackbar) => (
        <Snackbar
          key={snackbar.id}
          open={true}
          autoHideDuration={snackbar.autoHideDuration}
          onClose={() => handleClose(snackbar.id)}
          anchorOrigin={{ vertical: "top", horizontal: "right" }}
          sx={{
            mt: snackbars.indexOf(snackbar) * 8,
            zIndex: 9999 + snackbars.indexOf(snackbar)
          }}
        >
          <Alert
            onClose={() => handleClose(snackbar.id)}
            severity={snackbar.severity}
            variant="filled"
            sx={{ width: "100%" }}
          >
            {snackbar.message}
          </Alert>
        </Snackbar>
      ))}
    </Provider>
  );
}
