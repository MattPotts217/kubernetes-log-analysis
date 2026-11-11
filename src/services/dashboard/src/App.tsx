import './App.scss'
import AlertsTable from './components/AlertsTable/AlertsTable'
import ShellBar from './components/shellbar/ShellBar'

function App() {

  return (
    <>
      <ShellBar />
      <div className='table'>
        <AlertsTable />
      </div>
    </>
  )
}

export default App
