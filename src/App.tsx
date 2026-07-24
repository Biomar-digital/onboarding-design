import { Navigate, Route, Routes } from "react-router-dom";
import { useStore } from "./lib/store";
import { Layout } from "./components/Layout";
import { Login } from "./pages/Login";
import { Employee } from "./pages/Employee";
import { ModuleView } from "./pages/ModuleView";
import { Admin } from "./pages/Admin";
import { AdminPerson } from "./pages/AdminPerson";
import type { ReactNode } from "react";

function Require({
  children,
  role,
}: {
  children: ReactNode;
  role?: "admin" | "employee";
}) {
  const { currentUser } = useStore();
  if (!currentUser) return <Navigate to="/login" replace />;
  if (role && currentUser.role !== role)
    return <Navigate to={currentUser.role === "admin" ? "/admin" : "/"} replace />;
  return <>{children}</>;
}

export default function App() {
  const { currentUser } = useStore();

  return (
    <Routes>
      <Route
        path="/login"
        element={
          currentUser ? (
            <Navigate to={currentUser.role === "admin" ? "/admin" : "/"} replace />
          ) : (
            <Login />
          )
        }
      />

      <Route
        path="/"
        element={
          !currentUser ? (
            <Navigate to="/login" replace />
          ) : currentUser.role === "admin" ? (
            <Navigate to="/admin" replace />
          ) : (
            <Layout>
              <Employee />
            </Layout>
          )
        }
      />

      <Route
        path="/module/:moduleId"
        element={
          <Require role="employee">
            <Layout>
              <ModuleView />
            </Layout>
          </Require>
        }
      />

      <Route
        path="/admin"
        element={
          <Require role="admin">
            <Layout>
              <Admin />
            </Layout>
          </Require>
        }
      />
      <Route
        path="/admin/new"
        element={
          <Require role="admin">
            <Layout>
              <AdminPerson mode="new" />
            </Layout>
          </Require>
        }
      />
      <Route
        path="/admin/person/:id"
        element={
          <Require role="admin">
            <Layout>
              <AdminPerson mode="edit" />
            </Layout>
          </Require>
        }
      />

      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  );
}
