import { useContext } from 'react'
import ConfigContext from '../contexts/ConfigContext'
export const useConfig = () => useContext(ConfigContext);