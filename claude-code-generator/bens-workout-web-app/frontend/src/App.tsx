import { useState } from 'react'
import Header from './components/Header'
import './App.css'

function App() {
  const [count, setCount] = useState(0)

  return (
    <>
      <Header />
      <div className="container">
        <h1>Bens Workout Web App</h1>
        <p>it is a web app about fitness. It will have a sign in for users, account, video tutorials, users can also track their progress, meals, calories, metrics. There will also be a leaderboard of all users.</p>

        <div className="card">
          <button onClick={() => setCount((count) => count + 1)}>
            count is {count}
          </button>
          <p>
            Edit <code>src/App.tsx</code> and save to test HMR
          </p>
        </div>

        <div className="info">
          <h2>Get Started</h2>
          <p>Check out the <code>.claude/</code> directory for development guides and agents.</p>
        </div>
      </div>
    </>
  )
}

export default App
