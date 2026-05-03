import { RouteObject } from "react-router-dom";
import { Layout } from "./layout";
import Home from "./pages/Home";
import Login from "./pages/Login";
import Register from "./pages/Register";
import Square from "./pages/Square";
import Discovery from "./pages/Discovery";
import Profile from "./pages/Profile";
import OPCDetail from "./pages/OPCDetail";

export const routes: RouteObject[] = [
  {
    element: <Layout />,
    children: [
      {
        path: "/",
        element: <Home />,
      },
      {
        path: "/login",
        element: <Login />,
      },
      {
        path: "/register",
        element: <Register />,
      },
      {
        path: "/square",
        element: <Square />,
      },
      {
        path: "/discovery",
        element: <Discovery />,
      },
      {
        path: "/profile",
        element: <Profile />,
      },
      {
        path: "/opc/:id",
        element: <OPCDetail />,
      },
      {
        path: "*",
        element: <Home />,
      },
    ],
  },
];
