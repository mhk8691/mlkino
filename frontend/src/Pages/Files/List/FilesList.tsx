import {useSearchParams} from 'react-router-dom'
import {RecordList} from '../RecordList'
import AdvancedPropertyResults from '../AdvancedPropertyResults'
export function FilesList(){const [params]=useSearchParams();return params.get('advanced')==='1'?<AdvancedPropertyResults/>:<RecordList mode="file"/>}
