import { createBrowserRouter } from "react-router-dom";
import AppLayout from "../components/layout/AppLayout";
import ProtectedRoute from "../components/auth/ProtectedRoute";

import VerifyPage from "../pages/VerifyPage";
import OCRReviewPage from "../pages/OCRReviewPage";
import ClaimSelectionPage from "../pages/ClaimSelectionPage";
import VerificationProgressPage from "../pages/VerificationProgressPage";
import ResultPage from "../pages/ResultPage";
import TimelinePage from "../pages/TimelinePage";
import EvidencePage from "../pages/EvidencePage";
import EvidenceDetailPage from "../pages/EvidenceDetailPage";
import HistoryPage from "../pages/HistoryPage";
import HowItWorksPage from "../pages/HowItWorksPage";
import LoginPage from "../pages/LoginPage";
import RegisterPage from "../pages/RegisterPage";

const router = createBrowserRouter([
  {
    element: <AppLayout />,
    children: [
      {
        path: "/",
        element: <VerifyPage />,
      },
      {
        path: "/ocr-review",
        element: <OCRReviewPage />,
      },
      {
        path: "/claims",
        element: <ClaimSelectionPage />,
      },
      {
        path: "/progress",
        element: <VerificationProgressPage />,
      },
      {
        path: "/result/:id",
        element: <ResultPage />,
      },
      {
        path: "/timeline",
        element: <TimelinePage />,
      },
      {
        path: "/evidence",
        element: <EvidencePage />,
      },
      {
        path: "/evidence/:id",
        element: <EvidenceDetailPage />,
      },
      {
        path: "/how-it-works",
        element: <HowItWorksPage />,
      },
      {
        path: "/login",
        element: <LoginPage />,
      },
      {
        path: "/register",
        element: <RegisterPage />,
      },

      // Protected pages
      {
        element: <ProtectedRoute />,
        children: [
          {
            path: "/history",
            element: <HistoryPage />,
          },
        ],
      },
    ],
  },
]);

export default router;
