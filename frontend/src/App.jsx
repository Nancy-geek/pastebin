import { BrowserRouter, Routes, Route } from 'react-router-dom'
import CreatePaste from './components/CreatePaste'
import ViewPaste from './components/ViewPaste'
import './App.css'

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<CreatePaste />} />
        <Route path="/p/:pasteId" element={<ViewPaste />} />
      </Routes>
    </BrowserRouter>
  )
}

export default App
