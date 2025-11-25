export default function Header() {
  return (
    <header style={{
      borderBottom: '1px solid #333',
      padding: '1rem 2rem',
      marginBottom: '2rem'
    }}>
      <nav style={{
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'center',
        maxWidth: '1200px',
        margin: '0 auto'
      }}>
        <h2 style={{ margin: 0 }}>Enhanced Test SaaS</h2>
        <ul style={{
          display: 'flex',
          gap: '2rem',
          listStyle: 'none',
          margin: 0,
          padding: 0
        }}>
          <li><a href="/">Home</a></li>
          <li><a href="/about">About</a></li>
        </ul>
      </nav>
    </header>
  )
}
