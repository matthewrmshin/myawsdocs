program hello
character(64) :: who = 'World'
logical :: who_nl_exists
namelist /who_nl/ who
inquire(file='who.nl', exist=who_nl_exists)
if (who_nl_exists) then
  open(10, file='who.nl')
  read(10, nml=who_nl)
  close(10)
end if
write(*, '(a,1x,a,a)') 'Hello', trim(who), '!'
end program hello
