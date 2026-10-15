import { BrowserRouter, Navigate, Route, Routes } from 'react-router-dom'

import { AppShell } from '@/components/layout/AppShell'
import { AnomaliesPage } from '@/pages/AnomaliesPage'
import { DependenciesPage } from '@/pages/DependenciesPage'
import { OverviewPage } from '@/pages/OverviewPage'
import { PeoplePage } from '@/pages/PeoplePage'
import { ProgressPage } from '@/pages/ProgressPage'

export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route element={<AppShell />}>
          <Route index element={<OverviewPage />} />
          <Route path="progress" element={<ProgressPage />} />
          <Route path="dependencies" element={<DependenciesPage />} />
          <Route path="anomalies" element={<AnomaliesPage />} />
          <Route path="people" element={<PeoplePage />} />
          <Route path="*" element={<Navigate to="/" replace />} />
        </Route>
      </Routes>
    </BrowserRouter>
  )
}
