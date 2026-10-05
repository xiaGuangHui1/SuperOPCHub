import { RouteObject } from "react-router-dom";
import { Layout } from "./layout";
import Home from "./pages/Home";
import Square from "./pages/Square";
import Discovery from "./pages/Discovery";
import Profile from "./pages/Profile";
import OPCDetail from "./pages/OPCDetail";
import Record from "./pages/Record";

export const routes: RouteObject[] = [
  {
    element: <Layout />,
    children: [
      { path: "/", element: <Home /> },
      { path: "/square", element: <Square /> },
      { path: "/discovery", element: <Discovery /> },
      { path: "/profile", element: <Profile /> },
      { path: "/opc/:id", element: <OPCDetail /> },
      { path: "/record", element: <Record /> },
      { path: "*", element: <Home /> },
    ],
  },
];
